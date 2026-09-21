from __future__ import annotations

import argparse
from pathlib import Path

FINAL_MARKER = "USER:\nUsing these APIs, now generate code to solve the actual task:\n"

CONTROL_TEXT = """## Private prior experience
No validated private experience is available from earlier tasks.
"""

TREATMENT_PREFIX = """## Private prior experience
The following evidence was earned from this worker's own earlier task interactions.
It is scoped procedural evidence, not an answer to the current task.
Do not reuse concrete old entity values, credentials, paths, or IDs.
Re-bind all arguments from the current task and current app state.

"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-prompt", required=True)
    ap.add_argument("--mode", choices=["control", "experience"], required=True)
    ap.add_argument("--experience-file")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    base = Path(args.base_prompt).read_text(encoding="utf-8")
    if FINAL_MARKER not in base:
        raise SystemExit("Final AppWorld task marker not found")

    if args.mode == "control":
        section = CONTROL_TEXT
    else:
        if not args.experience_file:
            raise SystemExit("--experience-file is required in experience mode")
        experience = Path(args.experience_file).read_text(encoding="utf-8").strip()
        if not experience:
            raise SystemExit("experience file is empty")
        section = TREATMENT_PREFIX + experience + "\n"

    prompt = base.replace(FINAL_MARKER, FINAL_MARKER + "\n" + section + "\n", 1)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
