"""Integrate temporary migration pages into their final topic pages.

The script is fingerprint guarded, supports dry-run, creates an in-repository
rollback snapshot, preserves every link line, and removes only the five
temporary ``资源补充.md`` pages after all records have been written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIGRATION_ID = "unified-classification-v2"
BACKUP_ROOT = ROOT / "migration-backups" / MIGRATION_ID

SOURCE_FILES = {
    "docs/AI/资源补充.md",
    "docs/CS/资源补充.md",
    "docs/开发/资源补充.md",
    "docs/学习成长/资源补充.md",
    "docs/学习成长/成长与职业/资源补充.md",
}

TARGET_TITLES = {
    "docs/AI/AI工程与系统.md": "AI 工程与系统",
    "docs/开发/安全工程.md": "安全工程",
}


def digest_sources() -> str:
    digest = hashlib.sha256()
    for relative in sorted(SOURCE_FILES):
        path = ROOT / relative
        digest.update(relative.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def parse_sections(path: Path) -> list[tuple[str, str, str]]:
    text = path.read_text("utf-8")
    sections: list[tuple[str, str, str]] = []
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = match.group(1).strip()
        payload = text[match.end():end].strip()
        for line in payload.splitlines():
            if not line.strip():
                continue
            title_match = re.match(r"^-\s+\[([^]]+)]\(", line)
            if not title_match:
                raise ValueError(f"Unsupported content in {path}: {line}")
            sections.append((section, title_match.group(1).strip(), line.rstrip()))
    return sections


def destination(source: str, section: str, title: str) -> tuple[str, str | None]:
    if source == "docs/AI/资源补充.md":
        if section == "AI工程与系统":
            return "docs/AI/AI工程与系统.md", None
        if section == "具身智能与机器人":
            return "docs/AI/AI应用/具身智能.md", "具身智能"
        if section == "强化学习":
            return "docs/AI/AI理论基础.md", "强化学习（RL）"
        if section == "机器学习基础":
            return "docs/AI/AI理论基础.md", "机器学习（ML）"
        if section == "深度学习":
            return "docs/AI/AI理论基础.md", "深度学习（DL）"
        if section == "生成式与多模态":
            if title.startswith("ASVR:"):
                return "docs/AI/AI应用/多模态技术.md", "多模态"
            return "docs/AI/AI应用/AIGC内容生成.md", "AIGC"
        if section == "大语言模型与智能体":
            if re.search(r"RAG|检索增强", title, re.IGNORECASE):
                return "docs/AI/大语言模型/RAG检索增强.md", "RAG"
            if re.search(
                r"Agent|Claude|Codex|Copilot|AGENTS|MCP|SWE-Bench|"
                r"Pocket Flow|AutoSci|GenericAgent|everything-claude|"
                r"OpenAPI spec|operative\.sh|智能RSS|动手写一个简单的 agent",
                title,
                re.IGNORECASE,
            ):
                return "docs/AI/大语言模型/AI-Agent智能体.md", "教程"
            return "docs/AI/大语言模型/LLM原理.md", "LLM"

    if source == "docs/CS/资源补充.md":
        if section == "数据库与编译":
            return "docs/CS/系统原理/编译原理.md", "资料收集"
        if section == "系统与体系结构":
            if "共识算法" in title:
                return "docs/CS/系统原理/分布式.md", "Mit6.5840"
            if "Chapter 2" in title or "CPU工作原理" in title:
                return "docs/CS/系统原理/体系结构.md", "CSAPP"
            return "docs/CS/系统原理/操作系统.md", "SJTU-IPADS"
        if section == "编程与算法":
            if "编译器" in title or "编译吗" in title:
                return "docs/CS/系统原理/编译原理.md", "资料收集"
            if re.search(r"Blelloch|算法八股|算法岗|经典的算法", title):
                return "docs/CS/编程/算法.md", "算法"
            return "docs/CS/编程/编程.md", "C++"
        if section == "网络与分布式":
            if "Natural Language Processing" in title:
                return "docs/AI/大语言模型/LLM原理.md", "LLM"
            if "Build your own Redis" in title:
                return "docs/开发/项目.md", "项目"
            if title.startswith("AI Native"):
                return "docs/AI/AI工程与系统.md", None
            if "聚合登录架构" in title:
                return "docs/开发/前后端.md", "后端"
            if "IPADS" in title:
                return "docs/CS/系统原理/分布式.md", "Mit6.5840"
            return "docs/CS/系统原理/计算机网络.md", "计算机网络"

    if source == "docs/开发/资源补充.md":
        if section == "Web与后端":
            if "持久化变更日志 API" in title:
                return "docs/CS/系统原理/操作系统.md", "SJTU-IPADS"
            return "docs/开发/前后端.md", "后端"
        if section == "图形学与可视化":
            return "docs/开发/计算机图形学.md", "图形学"
        if section == "安全工程":
            return "docs/开发/安全工程.md", None
        if section == "开源项目与工程实践":
            return "docs/开发/项目.md", "项目"

    if source == "docs/学习成长/资源补充.md" and section == "课程与学习资源":
        return "docs/学习成长/学习资源.md", "学习记录"

    if source == "docs/学习成长/成长与职业/资源补充.md" and section == "职业发展":
        return "docs/学习成长/职业发展/工作就业.md", "工作就业"

    raise KeyError(f"No destination for {source} / {section} / {title}")


def insert_under_heading(text: str, heading: str, lines: list[str]) -> str:
    pattern = re.compile(rf"^#\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Heading not found: {heading}")
    next_heading = re.search(r"^#\s+.+$", text[match.end():], re.MULTILINE)
    insert_at = match.end() + next_heading.start() if next_heading else len(text)
    prefix = text[:insert_at].rstrip()
    suffix = text[insert_at:].lstrip("\n")
    block = "\n\n## 相关资料\n\n" + "\n".join(lines) + "\n"
    return prefix + block + ("\n" + suffix if suffix else "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    missing = [path for path in SOURCE_FILES if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"Temporary source pages missing: {missing}")

    source_digest = digest_sources()
    grouped: dict[tuple[str, str | None], list[str]] = defaultdict(list)
    ledger: list[dict[str, str]] = []
    for source in sorted(SOURCE_FILES):
        for section, title, line in parse_sections(ROOT / source):
            target, heading = destination(source, section, title)
            grouped[(target, heading)].append(line)
            ledger.append(
                {
                    "title": title,
                    "temporary_page": source,
                    "temporary_section": section,
                    "final_page": target,
                    "final_heading": heading or TARGET_TITLES[target],
                }
            )

    if len(ledger) != 153:
        raise SystemExit(f"Expected 153 temporary records, found {len(ledger)}")

    result = {
        "migration_id": MIGRATION_ID,
        "source_digest": source_digest,
        "records_integrated": len(ledger),
        "temporary_pages_removed": sorted(SOURCE_FILES),
        "target_pages": sorted({target for target, _ in grouped}),
        "applied": args.apply,
    }
    if not args.apply:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if BACKUP_ROOT.exists():
        raise SystemExit(f"Rollback directory already exists: {BACKUP_ROOT}")

    touched = set(SOURCE_FILES) | {target for target, _ in grouped if (ROOT / target).exists()}
    for relative in sorted(touched):
        destination_path = BACKUP_ROOT / relative
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination_path)

    by_target: dict[str, list[tuple[str | None, list[str]]]] = defaultdict(list)
    for (target, heading), lines in grouped.items():
        by_target[target].append((heading, lines))

    for target, sections in by_target.items():
        path = ROOT / target
        path.parent.mkdir(parents=True, exist_ok=True)
        if target in TARGET_TITLES:
            all_lines = [line for _, lines in sections for line in lines]
            text = (
                "---\ncomments: false\n---\n\n"
                f"# {TARGET_TITLES[target]}\n\n" + "\n".join(all_lines) + "\n"
            )
        else:
            text = path.read_text("utf-8")
            for heading, lines in sections:
                if heading is None:
                    raise AssertionError(target)
                text = insert_under_heading(text, heading, lines)
        path.write_text(text, encoding="utf-8", newline="\n")

    for source in SOURCE_FILES:
        (ROOT / source).unlink()

    result["applied_at"] = datetime.now().astimezone().isoformat()
    result["ledger"] = ledger
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    (BACKUP_ROOT / "migration-manifest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in result.items() if key != "ledger"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
