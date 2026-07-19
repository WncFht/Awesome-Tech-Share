"""Apply the reviewed content plan with an in-repository rollback snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


MIGRATION_ID = "content-restructure-v1"
DESTINATIONS = {
    "计算机科学基础": "docs/CS/资源补充.md",
    "人工智能与机器人": "docs/AI/资源补充.md",
    "软件开发与工程": "docs/开发/资源补充.md",
    "学习与研究": "docs/学习成长/资源补充.md",
    "成长与职业": "docs/学习成长/成长与职业/资源补充.md",
}


def current_domain(path: str) -> str:
    if path.startswith("docs/CS/"):
        return "计算机科学基础"
    if path.startswith("docs/AI/"):
        return "人工智能与机器人"
    if path.startswith("docs/开发/"):
        return "软件开发与工程"
    if path.startswith("docs/总结/"):
        return "成长与职业"
    if path.startswith("docs/学习成长/职业发展/") or path.endswith("读书笔记.md"):
        return "成长与职业"
    if path.startswith("docs/学习成长/"):
        return "学习与研究"
    return ""


def digest_docs(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / "docs").rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0" + path.read_bytes())
    return digest.hexdigest()


def markdown_line(row: dict[str, str], moved_from: str | None = None) -> str:
    title = row["suggested_title"] or row["original_title"]
    description = row["suggested_description"]
    result = row["link_result"]
    line = f"- [{title}]({row['url']})"
    if description:
        line += f" — {description}"
    comments = []
    if moved_from:
        comments.append(f"migrated-from: {moved_from}; record-id: {row['record_id']}")
    if row["needs_manual_confirmation"].lower() == "true":
        comments.append(f"待人工确认: {result}; record-id: {row['record_id']}")
    if comments:
        line += " <!-- " + " | ".join(comments) + " -->"
    return line


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--plan", type=Path, default=Path("reports/content-audit/adjustment-plan.csv"))
    parser.add_argument("--inventory", type=Path, default=Path("reports/content-audit/source-inventory.json"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    root = args.project_root.resolve()
    if (root / "migration-backups/unified-classification-v2/migration-manifest.json").is_file():
        raise SystemExit(
            "content-restructure-v1 已被 unified-classification-v2 取代；"
            "禁止重新生成临时‘资源补充’页面。"
        )
    plan_path = args.plan if args.plan.is_absolute() else root / args.plan
    inventory_path = args.inventory if args.inventory.is_absolute() else root / args.inventory
    plan = list(csv.DictReader(plan_path.open(encoding="utf-8-sig")))
    inventory = json.loads(inventory_path.read_text("utf-8"))
    expected_digest = inventory["metadata"]["source_digest"]
    actual_digest = digest_docs(root)
    if actual_digest != expected_digest:
        raise SystemExit(
            "Source Markdown changed after the adjustment plan was generated; regenerate the audit before migration."
        )

    line_groups: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in plan:
        line_groups[(row["source_path"], int(row["source_line"]))].append(row)

    source_lines: dict[str, list[str]] = {}
    moved: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    fixed_in_place = 0
    moved_count = 0
    skipped_complex = 0
    modified_sources: set[str] = set()

    for (source_path, line_number), rows in sorted(line_groups.items()):
        if len(rows) != 1 or rows[0]["parse_status"] not in {"valid", "recovered"}:
            continue
        row = rows[0]
        proposed_top, proposed_sub = row["suggested_category"].split(" / ", 1)
        should_move = proposed_top in DESTINATIONS and proposed_top != current_domain(source_path)
        has_fix = any(
            action in row["actions"]
            for action in ("update_title", "update_description", "fix_syntax")
        )
        if not should_move and not has_fix:
            continue
        path = root / source_path
        lines = source_lines.setdefault(source_path, path.read_text("utf-8").splitlines())
        index = line_number - 1
        if index >= len(lines):
            raise SystemExit(f"Line out of range: {source_path}:{line_number}")
        original_line = lines[index]
        if "http" not in original_line or original_line.lstrip().startswith("<"):
            skipped_complex += 1
            continue
        if should_move:
            destination = DESTINATIONS[proposed_top]
            moved[destination][proposed_sub].append(row)
            lines[index] = ""
            moved_count += 1
        else:
            lines[index] = markdown_line(row)
            fixed_in_place += 1
        modified_sources.add(source_path)

    generated: dict[str, str] = {}
    for destination, sections in sorted(moved.items()):
        title = Path(destination).parent.name + "资源补充"
        chunks = [
            "---",
            "comments: false",
            "---",
            "",
            f"# {title}",
            "",
            "本页内容由原分类页面按主要主题迁移而来。原位置、记录 ID 与需人工确认状态保存在行尾注释及调整清单中。",
            "",
        ]
        for section, rows in sorted(sections.items()):
            chunks.extend([f"## {section}", ""])
            for row in sorted(rows, key=lambda item: (item["source_path"], int(item["source_line"]))):
                chunks.append(markdown_line(row, f"{row['source_path']}:{row['source_line']}"))
            chunks.append("")
        generated[destination] = "\n".join(chunks).rstrip() + "\n"

    summary = {
        "migration_id": MIGRATION_ID,
        "source_digest": actual_digest,
        "plan_records": len(plan),
        "moved_records": moved_count,
        "fixed_in_place_records": fixed_in_place,
        "skipped_complex_records": skipped_complex,
        "modified_source_files": sorted(modified_sources),
        "generated_files": sorted(generated),
    }
    if not args.apply:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    backup_root = root / "migration-backups" / MIGRATION_ID
    if backup_root.exists():
        raise SystemExit(f"Migration backup already exists: {backup_root}")
    for source_path in sorted(modified_sources):
        source = root / source_path
        backup = backup_root / source_path
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup)
    for destination in generated:
        if (root / destination).exists():
            raise SystemExit(f"Generated destination already exists: {destination}")

    for source_path, lines in source_lines.items():
        if source_path not in modified_sources:
            continue
        # Collapse no more than two consecutive blank lines after moved list items.
        cooked: list[str] = []
        for line in lines:
            if not line and len(cooked) >= 2 and cooked[-1] == cooked[-2] == "":
                continue
            cooked.append(line)
        (root / source_path).write_text("\n".join(cooked).rstrip() + "\n", encoding="utf-8")
    for destination, content in generated.items():
        path = root / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    summary["applied_at"] = datetime.now().astimezone().isoformat()
    (backup_root / "migration-manifest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
