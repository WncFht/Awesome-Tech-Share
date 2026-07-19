"""Validate zero-loss content migration against the pre-migration ledger."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from content_audit import normalize_url


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    before = json.loads((ROOT / "reports/content-audit/source-inventory.json").read_text("utf-8"))
    after = json.loads((ROOT / "reports/post-migration/source-inventory.json").read_text("utf-8"))
    plan = list(
        csv.DictReader(
            (ROOT / "reports/content-audit/adjustment-plan.csv").open(encoding="utf-8-sig")
        )
    )
    manifest = json.loads(
        (ROOT / "migration-backups/content-restructure-v1/migration-manifest.json").read_text("utf-8")
    )
    unified_manifest = json.loads(
        (ROOT / "migration-backups/unified-classification-v2/migration-manifest.json").read_text("utf-8")
    )

    before_urls = Counter(row["normalized_url"] for row in before["records"])
    after_urls = Counter(row["normalized_url"] for row in after["records"])
    expected_titles = Counter(
        (normalize_url(row["url"]), row["suggested_title"] or row["original_title"])
        for row in plan
    )
    after_titles = Counter(
        (row["normalized_url"], row["original_title"]) for row in after["records"]
    )
    expected_descriptions = Counter(
        (normalize_url(row["url"]), row["suggested_description"]) for row in plan
    )
    after_descriptions = Counter(
        (row["normalized_url"], row["original_description"]) for row in after["records"]
    )
    final_text = "\n".join(
        (ROOT / path).read_text("utf-8") for path in unified_manifest["target_pages"]
    )
    mkdocs_text = (ROOT / "mkdocs.yml").read_text("utf-8")

    checks = {
        "record_count_equal": before["metadata"]["records"] == after["metadata"]["records"] == len(plan),
        "url_multiset_equal": before_urls == after_urls,
        "title_multiset_matches_plan": expected_titles == after_titles,
        "description_multiset_matches_plan": expected_descriptions == after_descriptions,
        "no_recovered_malformed_records": after["metadata"]["recovered_records"] == 0,
        "all_moved_records_traceable": final_text.count("migrated-from:") == manifest["moved_records"],
        "migration_backup_complete": all(
            (ROOT / "migration-backups/content-restructure-v1" / path).is_file()
            for path in manifest["modified_source_files"]
        ),
        "temporary_migration_pages_removed": all(
            not (ROOT / path).exists() for path in unified_manifest["temporary_pages_removed"]
        ),
        "all_final_target_pages_present": all(
            (ROOT / path).is_file() for path in unified_manifest["target_pages"]
        ),
        "all_temporary_records_integrated": unified_manifest["records_integrated"] == manifest["moved_records"],
        "temporary_navigation_removed": "主题迁入资源" not in mkdocs_text and "资源补充.md" not in mkdocs_text,
    }
    result = {
        "before": before["metadata"],
        "after": after["metadata"],
        "migration": manifest,
        "unified_classification": {
            key: value for key, value in unified_manifest.items() if key != "ledger"
        },
        "checks": checks,
        "verified": all(checks.values()),
    }
    output = ROOT / "reports/post-migration/validation.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ledger_output = ROOT / "reports/post-migration/unified-classification-ledger.csv"
    with ledger_output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(unified_manifest["ledger"][0]))
        writer.writeheader()
        writer.writerows(unified_manifest["ledger"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
