"""Report truly empty Markdown headings and pages without visible content."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FRONT_MATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)


def visible_payload(value: str) -> str:
    value = COMMENT.sub("", value)
    value = HEADING.sub("", value)
    return value.strip()


def main() -> int:
    empty_sections: list[dict[str, object]] = []
    empty_pages: list[str] = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
        text = path.read_text("utf-8")
        body = FRONT_MATTER.sub("", text)
        headings = list(HEADING.finditer(body))
        for index, match in enumerate(headings):
            level = len(match.group(1))
            end = len(body)
            for candidate in headings[index + 1:]:
                if len(candidate.group(1)) <= level:
                    end = candidate.start()
                    break
            if not visible_payload(body[match.end():end]):
                line = body.count("\n", 0, match.start()) + 1
                empty_sections.append(
                    {
                        "path": path.relative_to(ROOT).as_posix(),
                        "line": line,
                        "level": level,
                        "title": match.group(2),
                    }
                )
        if not visible_payload(body):
            empty_pages.append(path.relative_to(ROOT).as_posix())

    result = {"empty_sections": empty_sections, "empty_pages": empty_pages}
    output = ROOT / "reports/post-migration/empty-content-audit.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
