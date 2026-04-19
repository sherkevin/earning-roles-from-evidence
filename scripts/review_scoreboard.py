from __future__ import annotations

import json
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = ROOT / "artifacts" / "idea_reviews"


def main() -> None:
    index_path = ARCHIVE_ROOT / "review_index.jsonl"
    rows = []
    if index_path.is_file():
        with index_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    valid = [r for r in rows if r.get("overall_score") is not None]
    parseable = [r for r in rows if r.get("verdict") not in {"parse_failed", None}]
    lines = ["# Reviewer Scoreboard", ""]
    lines.append(f"- total_reviews: {len(rows)}")
    lines.append(f"- parseable_reviews: {len(parseable)}")
    lines.append(f"- scored_reviews: {len(valid)}")
    if rows:
        lines.append(f"- parseable_rate: {len(parseable) / len(rows):.3f}")
    if valid:
        lines.append(f"- average_overall: {mean(float(r['overall_score']) for r in valid):.3f}")
        lines.append(f"- latest_overall: {valid[-1]['overall_score']}")
    lines.append("")
    lines.append("## Latest Scored Reviews")
    lines.append("")
    for row in valid[-10:]:
        lines.append(
            f"- {row['review_run_id']}: overall={row['overall_score']}, verdict={row.get('verdict')}, model={row.get('model')}"
        )
    out_path = ARCHIVE_ROOT / "scoreboard.md"
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
