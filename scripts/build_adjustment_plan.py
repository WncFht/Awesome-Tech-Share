"""Build the full, reviewable adjustment ledger without changing Markdown."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


GENERIC_PAGE_TITLES = (
    "just a moment",
    "百度安全验证",
    "知乎 -",
    "哔哩哔哩",
    "search code, repositories",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text("utf-8"))


def classify(record: dict[str, Any], rules: dict[str, Any]) -> tuple[str, str, str, str]:
    if record["top_category"] in {"首页", "贡献者", "标签"}:
        return "站点功能", record["top_category"], "utility", "high"

    for rule in rules.get("exact_record_rules", []):
        if (
            record["source_path"] == rule["source_path"]
            and int(record["source_line"]) == int(rule["source_line"])
        ):
            return (
                rule["category"],
                rule["subcategory"],
                "exact_record_rule",
                rule.get("confidence", "high"),
            )

    text = " ".join(
        [record["original_title"], record["original_description"], *record["heading_path"]]
    )
    for rule in rules["keyword_rules"]:
        if record["source_path"] in rule["scope_paths"] and re.search(
            rule["pattern"], text, re.IGNORECASE
        ):
            return (
                rule["category"],
                rule["subcategory"],
                f"keyword:{rule['pattern']}",
                "medium",
            )

    page_headings = rules["heading_rules"].get(record["source_path"], {})
    for heading in record["heading_path"]:
        if heading in page_headings:
            category, subcategory = page_headings[heading]
            return category, subcategory, f"heading:{heading}", "high"

    for rule in rules["direct_source_rules"]:
        if rule["path_contains"] in record["source_path"]:
            return (
                rule["category"],
                rule["subcategory"],
                f"source:{rule['path_contains']}",
                "high",
            )

    for rule in rules["fallback_rules"]:
        if record["source_path"] == rule["path"]:
            confidence = "medium" if record["source_path"] in {
                "docs/开发/项目.md", "docs/开发/开发工具.md"
            } else "low"
            return rule["category"], rule["subcategory"], "fallback", confidence

    return "待人工确认", "待人工确认", "unclassified", "low"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=Path("reports/content-audit/source-inventory.json"))
    parser.add_argument("--checks", type=Path, default=Path("reports/content-audit/link-check-results.json"))
    parser.add_argument("--rules", type=Path, default=Path("content-governance/classification-rules.json"))
    parser.add_argument("--fixes", type=Path, default=Path("content-governance/content-fixes.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/content-audit"))
    args = parser.parse_args()

    inventory = load_json(args.inventory)
    checks_payload = load_json(args.checks)
    rules = load_json(args.rules)
    fixes_payload = load_json(args.fixes)
    checks = {row["normalized_url"]: row for row in checks_payload["checks"]}
    fixes = {
        (row["source_path"], int(row["source_line"])): row
        for row in fixes_payload["fixes"]
    }
    records = inventory["records"]

    exact_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        exact_groups[record["normalized_url"]].append(record)
    exact_canonical = {
        url: min(group, key=lambda item: (item["top_category"] in {"总结", "学习成长"}, item["source_path"], item["source_line"]))
        for url, group in exact_groups.items()
        if len(group) > 1
    }
    final_groups: dict[str, set[str]] = defaultdict(set)
    for check in checks.values():
        if check["normalized_final_url"]:
            final_groups[check["normalized_final_url"]].add(check["normalized_url"])
    redirect_aliases = {
        original
        for group in final_groups.values()
        if len(group) > 1
        for original in group
    }

    plan: list[dict[str, Any]] = []
    for record in records:
        category, subcategory, classification_reason, confidence = classify(record, rules)
        check = checks.get(record["normalized_url"], {})
        fix = fixes.get((record["source_path"], int(record["source_line"])), {})
        suggested_title = fix.get("suggested_title") or record["original_title"]
        suggested_description = (
            fix["suggested_description"]
            if "suggested_description" in fix
            else record["original_description"]
        )

        actual_title = check.get("page_title", "")
        similarity = ""
        if actual_title and record["original_title"]:
            compact_original = re.sub(r"\W+", "", record["original_title"]).lower()
            compact_actual = re.sub(r"\W+", "", actual_title).lower()
            if compact_original and compact_actual:
                from difflib import SequenceMatcher
                similarity = round(SequenceMatcher(None, compact_original, compact_actual).ratio(), 3)
        title_review = bool(
            check.get("result") == "accessible"
            and actual_title
            and isinstance(similarity, float)
            and similarity < 0.28
            and not any(marker in actual_title.lower() for marker in GENERIC_PAGE_TITLES)
        )

        group = exact_groups[record["normalized_url"]]
        duplicate_role = ""
        if len(group) > 1:
            duplicate_role = (
                "canonical"
                if exact_canonical[record["normalized_url"]]["record_id"] == record["record_id"]
                else "duplicate"
            )
        manual = bool(
            check.get("needs_manual_confirmation")
            or confidence == "low"
            or record["parse_status"] != "valid"
            or duplicate_role
            or record["normalized_url"] in redirect_aliases
            or title_review
            or fix.get("manual_confirmation")
        )

        actions: list[str] = []
        proposed_full_category = f"{category} / {subcategory}"
        if category != "站点功能":
            actions.append("reclassify")
        if suggested_title != record["original_title"]:
            actions.append("update_title")
        if suggested_description != record["original_description"]:
            actions.append("update_description")
        if fix.get("syntax_fix"):
            actions.append("fix_syntax")
        if duplicate_role:
            actions.append("review_duplicate")
        if manual:
            actions.append("manual_confirmation")
        if not actions:
            actions.append("keep")

        reasons = [
            f"分类规则：{classification_reason}",
            fix.get("reason", ""),
        ]
        if check.get("result") != "accessible":
            reasons.append(f"链接检查：{check.get('result', 'unknown')}")
        if title_review:
            reasons.append("原标题与可访问页面标题相似度较低")
        if duplicate_role:
            reasons.append(f"完全相同 URL：{duplicate_role}")
        if record["normalized_url"] in redirect_aliases:
            reasons.append("不同地址重定向到同一目标")

        plan.append(
            {
                "record_id": record["record_id"],
                "source_path": record["source_path"],
                "source_line": record["source_line"],
                "url": record["url"],
                "original_title": record["original_title"],
                "suggested_title": suggested_title,
                "original_description": record["original_description"],
                "suggested_description": suggested_description,
                "original_category": record["original_category"],
                "suggested_category": proposed_full_category,
                "classification_confidence": confidence,
                "adjustment_reason": "；".join(reason for reason in reasons if reason),
                "actions": ",".join(actions),
                "needs_manual_confirmation": manual,
                "link_result": check.get("result", "unknown"),
                "status_code": check.get("status_code", ""),
                "final_url": check.get("final_url", ""),
                "actual_page_title": actual_title,
                "actual_page_h1": check.get("page_h1", ""),
                "actual_page_description": check.get("page_description", ""),
                "title_similarity": similarity,
                "duplicate_role": duplicate_role,
                "duplicate_of": fix.get("duplicate_of", ""),
                "parse_status": record["parse_status"],
            }
        )

    output = args.output_dir
    fields = list(plan[0].keys())
    write_csv(output / "adjustment-plan.csv", plan, fields)
    write_csv(output / "manual-review-plan.csv", [row for row in plan if row["needs_manual_confirmation"]], fields)
    write_csv(output / "title-change-plan.csv", [row for row in plan if "update_title" in row["actions"]], fields)
    write_csv(output / "description-change-plan.csv", [row for row in plan if "update_description" in row["actions"]], fields)

    mapping_counts = Counter((row["original_category"], row["suggested_category"]) for row in plan)
    mapping_rows = [
        {"original_category": old, "suggested_category": new, "records": count}
        for (old, new), count in sorted(mapping_counts.items())
    ]
    write_csv(output / "category-mapping-summary.csv", mapping_rows, ["original_category", "suggested_category", "records"])
    new_counts = Counter(row["suggested_category"] for row in plan)
    old_counts = Counter(row["original_category"] for row in plan)

    summary = {
        "source_records": len(plan),
        "planned_records": len(plan),
        "zero_unmapped": all(row["suggested_category"] for row in plan),
        "manual_confirmation_records": sum(row["needs_manual_confirmation"] for row in plan),
        "high_confidence_classifications": sum(row["classification_confidence"] == "high" for row in plan),
        "medium_confidence_classifications": sum(row["classification_confidence"] == "medium" for row in plan),
        "low_confidence_classifications": sum(row["classification_confidence"] == "low" for row in plan),
        "planned_title_changes": sum("update_title" in row["actions"] for row in plan),
        "planned_description_changes": sum("update_description" in row["actions"] for row in plan),
        "planned_syntax_fixes": sum("fix_syntax" in row["actions"] for row in plan),
        "exact_duplicate_records": sum(bool(row["duplicate_role"]) for row in plan),
        "old_category_paths": len(old_counts),
        "new_category_paths": len(new_counts),
        "new_category_counts": dict(sorted(new_counts.items())),
        "link_check_summary": checks_payload["summary"],
    }
    (output / "adjustment-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
