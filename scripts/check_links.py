"""Check every unique external URL without modifying source content.

Results are resumable and deliberately conservative: inaccessible, blocked,
rate-limited, or script-only pages are marked for manual confirmation rather
than treated as dead content.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import ssl
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 "
    "Awesome-Tech-Share-Link-Audit/1.0"
)
TITLE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
META = re.compile(r"<meta\b[^>]*>", re.IGNORECASE)
ATTRIBUTE = re.compile(
    r"(?P<name>[a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?P<quote>[\"'])(?P<value>.*?)(?P=quote)",
    re.DOTALL,
)
H1 = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
TAG = re.compile(r"<[^>]+>")
SPACE = re.compile(r"\s+")


def normalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, parts.query, parts.fragment)
    )


def clean_title(value: str) -> str:
    value = requests.utils.unquote_unreserved(value)
    value = TAG.sub(" ", value)
    return SPACE.sub(" ", value).strip()


def classify(status: int | None, error_type: str) -> tuple[str, bool]:
    if error_type:
        return error_type, True
    if status is None:
        return "network_error", True
    if 200 <= status < 400:
        return "accessible", False
    if status in {401, 403, 405, 407, 418, 429, 451}:
        return "access_restricted", True
    if status in {404, 410}:
        return "not_found", True
    if 400 <= status < 500:
        return "client_error", True
    if status >= 500:
        return "server_error", True
    return "unexpected_status", True


def fetch_url(url: str, timeout: float) -> dict[str, Any]:
    started = time.perf_counter()
    response: requests.Response | None = None
    status: int | None = None
    final_url = ""
    content_type = ""
    page_title = ""
    page_description = ""
    page_h1 = ""
    error = ""
    error_type = ""
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.5"},
            timeout=(5.0, timeout),
            allow_redirects=True,
            stream=True,
        )
        status = response.status_code
        final_url = response.url
        content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
        if "html" in content_type or not content_type:
            chunks: list[bytes] = []
            size = 0
            for chunk in response.iter_content(chunk_size=16384):
                if not chunk:
                    continue
                chunks.append(chunk)
                size += len(chunk)
                if size >= 262144:
                    break
            raw = b"".join(chunks)
            encoding = response.encoding or "utf-8"
            text = raw.decode(encoding, errors="replace")
            match = TITLE.search(text)
            if match:
                page_title = clean_title(match.group(1))
            h1_match = H1.search(text)
            if h1_match:
                page_h1 = clean_title(h1_match.group(1))
            for meta in META.findall(text):
                attributes = {
                    item.group("name").lower(): item.group("value")
                    for item in ATTRIBUTE.finditer(meta)
                }
                key = (attributes.get("name") or attributes.get("property") or "").lower()
                if key in {"description", "og:description", "twitter:description"} and attributes.get("content"):
                    page_description = clean_title(attributes["content"])
                    if key == "description":
                        break
    except requests.Timeout as exc:
        error_type, error = "timeout", str(exc)
    except requests.TooManyRedirects as exc:
        error_type, error = "redirect_error", str(exc)
    except requests.exceptions.SSLError as exc:
        error_type, error = "tls_error", str(exc)
    except (requests.ConnectionError, requests.RequestException, ssl.SSLError) as exc:
        error_type, error = "network_error", str(exc)
    except Exception as exc:  # Keep the complete audit running for unusual sites.
        error_type, error = "unexpected_error", f"{type(exc).__name__}: {exc}"
    finally:
        if response is not None:
            response.close()

    result, needs_manual = classify(status, error_type)
    visible_status = f"{page_title} {page_h1}".lower()
    if result == "accessible" and any(
        marker in visible_status
        for marker in ("404", "not found", "page not found", "页面不存在", "似乎你迷路了")
    ):
        result, needs_manual = "soft_not_found", True
    elif result == "accessible" and any(
        marker in visible_status
        for marker in ("just a moment", "安全验证", "security verification", "captcha")
    ):
        result, needs_manual = "access_restricted", True
    return {
        "url": url,
        "normalized_url": normalize_url(url),
        "checked_at": datetime.now().astimezone().isoformat(),
        "status_code": status if status is not None else "",
        "result": result,
        "needs_manual_confirmation": needs_manual,
        "final_url": final_url,
        "normalized_final_url": normalize_url(final_url) if final_url else "",
        "content_type": content_type,
        "page_title": page_title,
        "page_h1": page_h1,
        "page_description": page_description,
        "error": error[:600],
        "elapsed_ms": round((time.perf_counter() - started) * 1000),
    }


def title_similarity(original: str, actual: str) -> float | str:
    if not original or not actual:
        return ""
    strip = re.compile(r"[^0-9a-z\u4e00-\u9fff]+", re.IGNORECASE)
    left = strip.sub("", original).lower()
    right = strip.sub("", actual).lower()
    if not left or not right:
        return ""
    return round(SequenceMatcher(None, left, right).ratio(), 3)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=Path("reports/content-audit/source-inventory.json"))
    parser.add_argument("--output", type=Path, default=Path("reports/content-audit/link-check-results.json"))
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=12.0)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text("utf-8"))
    records = inventory["records"]
    urls = sorted({record["url"] for record in records})
    completed: dict[str, dict[str, Any]] = {}
    if args.resume and args.output.is_file():
        previous = json.loads(args.output.read_text("utf-8"))
        completed = {row["url"]: row for row in previous["checks"]}
    pending = [url for url in urls if url not in completed]

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(fetch_url, url, args.timeout): url for url in pending}
        for index, future in enumerate(as_completed(futures), 1):
            row = future.result()
            completed[row["url"]] = row
            if index % 50 == 0 or index == len(pending):
                print(f"checked {index}/{len(pending)} (total {len(completed)}/{len(urls)})", flush=True)

    checks = [completed[url] for url in urls]
    by_normalized = {row["normalized_url"]: row for row in checks}
    enriched: list[dict[str, Any]] = []
    for record in records:
        check = by_normalized.get(record["normalized_url"])
        if check is None:
            check = next((row for row in checks if row["url"] == record["url"]), None)
        combined = dict(record)
        if check:
            combined.update({f"check_{key}": value for key, value in check.items() if key not in {"url", "normalized_url"}})
            combined["title_similarity"] = title_similarity(record["original_title"], check["page_title"])
        enriched.append(combined)

    summary = dict(Counter(row["result"] for row in checks))
    payload = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "unique_urls": len(urls),
        "summary": summary,
        "checks": checks,
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    check_fields = list(checks[0].keys()) if checks else []
    write_csv(args.output.with_suffix(".csv"), checks, check_fields)
    manual = [row for row in enriched if row.get("check_needs_manual_confirmation")]
    manual_fields = [
        "record_id", "source_path", "source_line", "original_title", "original_description", "url",
        "original_category", "check_status_code", "check_result", "check_final_url", "check_page_title",
        "check_page_h1", "check_page_description", "check_error", "title_similarity",
    ]
    write_csv(args.output.parent / "manual-confirmation.csv", manual, manual_fields)

    title_candidates = [
        row for row in enriched
        if row.get("check_result") == "accessible"
        and row.get("check_page_title")
        and isinstance(row.get("title_similarity"), float)
        and row["title_similarity"] < 0.28
    ]
    write_csv(args.output.parent / "title-review-candidates.csv", title_candidates, manual_fields)

    final_groups: dict[str, list[dict[str, Any]]] = {}
    for row in enriched:
        final = row.get("check_normalized_final_url")
        if final:
            final_groups.setdefault(final, []).append(row)
    redirect_duplicates = [
        row
        for group in final_groups.values()
        if len({item["normalized_url"] for item in group}) > 1
        for row in group
    ]
    write_csv(args.output.parent / "redirect-duplicates.csv", redirect_duplicates, manual_fields)
    print(json.dumps({"unique_urls": len(urls), "summary": summary, "manual_records": len(manual), "title_review_candidates": len(title_candidates), "redirect_duplicate_records": len(redirect_duplicates)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
