from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = ROOT / "artifacts" / "idea_reviews"


def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip().lower())
    return text


def main() -> None:
    counter: Counter[str] = Counter()
    for review_path in ARCHIVE_ROOT.glob("reviewer_*/review.json"):
        review = json.loads(review_path.read_text(encoding="utf-8"))
        for key in (
            "top_weaknesses",
            "ambiguous_algorithm_points",
            "missing_or_weak_experiments",
            "what_to_fix_for_8_plus",
        ):
            for item in review.get(key) or []:
                norm = normalize(str(item))
                if norm:
                    counter[norm] += 1
    lines = ["# Fix Themes", ""]
    if not counter:
        lines.append("- no recurring themes extracted yet")
    else:
        for theme, count in counter.most_common(20):
            lines.append(f"- ({count}) {theme}")
    out_path = ARCHIVE_ROOT / "fix_themes.md"
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
