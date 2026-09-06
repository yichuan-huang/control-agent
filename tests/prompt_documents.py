"""Read the visible wizard tables in the bilingual dataset guides.

This deliberately contains no fallback answers: every draft value comes from
the document a user reads. Stable field identifiers disambiguate translated
labels, while JSON literals preserve numbers, checkboxes and signal row lists.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from cfdc.web.drafts import DRAFT_FIELDS


def read_prompt_document(path: Path) -> list[dict[str, Any]]:
    """Parse numbered entries, excluding the independent registered appendix."""
    text = path.read_text(encoding="utf-8")
    numbered = list(re.finditer(r"^## (\d+)\. (.+)$", text, re.MULTILINE))
    appendix = re.search(r"^## (?:Appendix:|附录：)", text, re.MULTILINE)
    entries = []
    for position, heading in enumerate(numbered):
        end = (
            numbered[position + 1].start()
            if position + 1 < len(numbered)
            else appendix.start()
            if appendix
            else len(text)
        )
        body = text[heading.end() : end]
        draft = read_draft_table(body)
        blocks = re.findall(r"^```text\n(.*?)\n```$", body, re.MULTILINE | re.DOTALL)
        if len(blocks) != 1:
            raise ValueError(f"one_diagnosis_block_required: {heading.group(1)}")
        source = re.search(r"control_problems\.md\).*?\[Ch\d+-\d+\]", body)
        if source is None:
            raise ValueError(f"source_required: {heading.group(1)}")
        entries.append(
            {
                "number": int(heading.group(1)),
                "title": heading.group(2),
                "draft": draft,
                "diagnosis": blocks[0],
                "source": source.group(),
                "text": body,
            }
        )
    return entries


def read_draft_table(text: str) -> dict[str, Any]:
    """Read exactly one complete visible draft, also used for case appendices."""
    draft = {}
    for key, literal in re.findall(
        r"^\| [^|]+ \| `([a-z_]+)` \| `(.*)` \|$", text, re.MULTILINE
    ):
        if key not in DRAFT_FIELDS:
            raise ValueError(f"unknown_draft_field: {key}")
        if key in draft:
            raise ValueError(f"duplicate_draft_field: {key}")
        draft[key] = json.loads(literal)
    if set(draft) != set(DRAFT_FIELDS):
        raise ValueError(f"draft_fields_missing: {set(DRAFT_FIELDS) - set(draft)}")
    return draft
