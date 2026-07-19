"""Create a traceable inventory of all existing Awesome Tech Share content.

This script is deliberately read-only with respect to ``docs/``. It extracts
records into ``reports/content-audit`` so classification proposals can be
reviewed before any source Markdown is changed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


TOP_CATEGORY_NAMES = {
    "AI": "人工智能",
    "CS": "计算机科学",
    "Tags": "标签",
    "links": "贡献者",
    "其他": "待整理",
    "学习成长": "学习成长",
    "开发": "开发",
    "总结": "总结",
}
MARKDOWN_LINK = re.compile(
    r"(?<!!)\[(?P<title>[^\]\n]+)\]\(\s*(?P<url>https?://[^)）]+?)\s*[)）]"
)
RECOVERABLE_LINK = re.compile(
    r"(?P<title>[^\[\]<>]{3,}?)\]\(\s*(?P<url>https?://[^)）]+?)\s*[)）]"
)
HTML_ANCHOR = re.compile(
    r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>", re.IGNORECASE | re.DOTALL
)
HTML_HREF = re.compile(r"href=[\"'](?P<url>https?://[^\"']+)[\"']", re.IGNORECASE)
HTML_TITLE = re.compile(r"title=[\"'](?P<title>[^\"']*)[\"']", re.IGNORECASE)
HTML_NAME = re.compile(
    r"class=[\"'][^\"']*flink-item-name[^\"']*[\"'][^>]*>(?P<text>.*?)</",
    re.IGNORECASE | re.DOTALL,
)
HTML_DESCRIPTION = re.compile(
    r"class=[\"'][^\"']*flink-item-desc[^\"']*[\"'][^>]*>(?P<text>.*?)</",
    re.IGNORECASE | re.DOTALL,
)
HEADING = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
TAG = re.compile(r"<[^>]+>")


def clean_display_text(value: str) -> str:
    return " ".join(html.unescape(TAG.sub(" ", value)).split()).strip()


def normalize_url(value: str) -> str:
    value = value.strip()
    parts = urlsplit(value)
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, parts.query, parts.fragment)
    )


def top_category(path: Path, docs_dir: Path) -> str:
    relative = path.relative_to(docs_dir)
    if len(relative.parts) == 1:
        return "首页" if relative.name == "index.md" else "其他"
    return TOP_CATEGORY_NAMES.get(relative.parts[0], relative.parts[0])


def heading_contexts(lines: list[str]) -> list[list[str]]:
    contexts: list[list[str]] = []
    stack: list[str] = []
    in_fence = False
    fence = ""
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence, fence = True, marker
            elif marker == fence:
                in_fence, fence = False, ""
        if not in_fence:
            match = HEADING.match(line)
            if match:
                level = len(match.group("marks"))
                stack = stack[: level - 1]
                stack.append(clean_display_text(match.group("title")))
        contexts.append(list(stack))
    return contexts


def page_title(path: Path, lines: list[str]) -> str:
    for line in lines:
        match = HEADING.match(line)
        if match and len(match.group("marks")) == 1:
            return clean_display_text(match.group("title"))
    return "首页" if path.name == "index.md" and path.parent.name == "docs" else path.stem


def description_after(line: str, end: int) -> str:
    tail = line[end:].strip()
    if not tail or tail.startswith(("/", "[")):
        return ""
    tail = tail.lstrip("-—–:：| ").strip()
    if not tail or tail in {"、", "/"} or "[" in tail:
        return ""
    return tail


def make_record(
    *,
    path: str,
    line: int,
    occurrence: int,
    title: str,
    url: str,
    description: str,
    category: str,
    page: str,
    headings: list[str],
    syntax: str,
    parse_status: str,
) -> dict[str, Any]:
    preserved_title = clean_display_text(title)
    preserved_description = clean_display_text(description)
    preserved_url = url.strip()
    signature = "\0".join(
        [path, str(line), str(occurrence), preserved_title, preserved_url]
    )
    return {
        "record_id": hashlib.sha256(signature.encode("utf-8")).hexdigest()[:16],
        "source_path": path,
        "source_line": line,
        "source_occurrence": occurrence,
        "original_title": preserved_title,
        "original_description": preserved_description,
        "url": preserved_url,
        "normalized_url": normalize_url(preserved_url),
        "domain": (urlsplit(preserved_url).hostname or "").lower().removeprefix("www."),
        "top_category": category,
        "page_title": page,
        "heading_path": headings,
        "original_category": " / ".join([category, page, *headings]).strip(" /"),
        "syntax": syntax,
        "parse_status": parse_status,
    }


def extract_records(project_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    docs_dir = project_root / "docs"
    records: list[dict[str, Any]] = []
    markdown_files = sorted(docs_dir.rglob("*.md"))
    source_digest = hashlib.sha256()
    heading_count = 0

    for path in markdown_files:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        lines = text.splitlines()
        relative = path.relative_to(project_root).as_posix()
        source_digest.update(relative.encode("utf-8") + b"\0" + raw)
        contexts = heading_contexts(lines)
        heading_count += sum(bool(HEADING.match(line)) for line in lines)
        category = top_category(path, docs_dir)
        page = page_title(path, lines)
        in_fence = False
        fence = ""

        for line_number, content in enumerate(lines, 1):
            stripped = content.lstrip()
            if stripped.startswith(("```", "~~~")):
                marker = stripped[:3]
                if not in_fence:
                    in_fence, fence = True, marker
                elif marker == fence:
                    in_fence, fence = False, ""
                continue
            if in_fence or "http" not in content or "<a" in content.lower():
                continue
            occupied: list[tuple[int, int]] = []
            occurrence = 0
            for match in MARKDOWN_LINK.finditer(content):
                occupied.append(match.span())
                records.append(
                    make_record(
                        path=relative,
                        line=line_number,
                        occurrence=occurrence,
                        title=match.group("title"),
                        url=match.group("url"),
                        description=description_after(content, match.end()),
                        category=category,
                        page=page,
                        headings=contexts[line_number - 1],
                        syntax="markdown",
                        parse_status="valid",
                    )
                )
                occurrence += 1
            for match in RECOVERABLE_LINK.finditer(content):
                if any(start <= match.start() < end for start, end in occupied):
                    continue
                records.append(
                    make_record(
                        path=relative,
                        line=line_number,
                        occurrence=occurrence,
                        title=match.group("title").lstrip("- "),
                        url=match.group("url"),
                        description="",
                        category=category,
                        page=page,
                        headings=contexts[line_number - 1],
                        syntax="markdown",
                        parse_status="recovered",
                    )
                )
                occurrence += 1

        for occurrence, match in enumerate(HTML_ANCHOR.finditer(text)):
            href = HTML_HREF.search(match.group("attrs"))
            if not href:
                continue
            line_number = text.count("\n", 0, match.start()) + 1
            name = HTML_NAME.search(match.group("body"))
            title_attr = HTML_TITLE.search(match.group("attrs"))
            description = HTML_DESCRIPTION.search(match.group("body"))
            title = (
                name.group("text")
                if name
                else title_attr.group("title")
                if title_attr
                else match.group("body")
            )
            records.append(
                make_record(
                    path=relative,
                    line=line_number,
                    occurrence=occurrence,
                    title=title,
                    url=href.group("url"),
                    description=description.group("text") if description else "",
                    category=category,
                    page=page,
                    headings=contexts[min(line_number - 1, len(contexts) - 1)],
                    syntax="html",
                    parse_status="valid",
                )
            )

    records.sort(
        key=lambda item: (
            item["source_path"],
            item["source_line"],
            item["source_occurrence"],
        )
    )
    url_counts = Counter(item["normalized_url"] for item in records)
    for item in records:
        item["exact_duplicate"] = url_counts[item["normalized_url"]] > 1

    metadata = {
        "source_digest": source_digest.hexdigest(),
        "markdown_files": len(markdown_files),
        "heading_count": heading_count,
        "records": len(records),
        "unique_urls": len(url_counts),
        "duplicate_occurrences": sum(count - 1 for count in url_counts.values() if count > 1),
        "descriptions": sum(bool(item["original_description"]) for item in records),
        "recovered_records": sum(item["parse_status"] == "recovered" for item in records),
        "top_categories": dict(Counter(item["top_category"] for item in records)),
    }
    return records, metadata


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            cooked = dict(row)
            if isinstance(cooked.get("heading_path"), list):
                cooked["heading_path"] = " / ".join(cooked["heading_path"])
            writer.writerow(cooked)


def generate_reports(project_root: Path, report_dir: Path) -> dict[str, Any]:
    records, metadata = extract_records(project_root)
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "source-inventory.json").write_text(
        json.dumps({"metadata": metadata, "records": records}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    fields = [
        "record_id",
        "source_path",
        "source_line",
        "source_occurrence",
        "original_title",
        "original_description",
        "url",
        "normalized_url",
        "domain",
        "top_category",
        "page_title",
        "heading_path",
        "original_category",
        "syntax",
        "parse_status",
        "exact_duplicate",
    ]
    write_csv(report_dir / "all-records.csv", records, fields)

    duplicates = [item for item in records if item["exact_duplicate"]]
    write_csv(report_dir / "exact-duplicates.csv", duplicates, fields)
    malformed = [item for item in records if item["parse_status"] != "valid"]
    write_csv(report_dir / "recovered-malformed-records.csv", malformed, fields)

    counts: dict[tuple[str, str, str], int] = Counter()
    for item in records:
        counts[(item["top_category"], item["page_title"], " / ".join(item["heading_path"]))] += 1
    count_rows = [
        {"top_category": key[0], "page_title": key[1], "heading_path": key[2], "records": value}
        for key, value in sorted(counts.items())
    ]
    write_csv(
        report_dir / "category-counts.csv",
        count_rows,
        ["top_category", "page_title", "heading_path", "records"],
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report-dir", type=Path, default=Path("reports/content-audit"))
    args = parser.parse_args()
    root = args.project_root.resolve()
    report_dir = args.report_dir if args.report_dir.is_absolute() else root / args.report_dir
    metadata = generate_reports(root, report_dir)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
