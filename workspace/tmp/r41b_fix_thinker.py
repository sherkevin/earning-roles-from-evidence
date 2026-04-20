"""Strip markdown code fences from thinker.py (upstream accident)."""
from pathlib import Path
p = Path("/media/data3/dengkw/idea04/external_baselines/reagent/Agent/thinker.py")
src = p.read_text(encoding="utf-8").rstrip()
if src.startswith("```"):
    # drop the first line
    src = src.split("\n", 1)[1]
# drop any trailing ``` fence
lines = src.rstrip().splitlines()
while lines and lines[-1].strip().startswith("```"):
    lines.pop()
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"cleaned {p}; now {sum(1 for _ in p.read_text(encoding='utf-8').splitlines())} lines")
print("head:", p.read_text(encoding="utf-8").splitlines()[0][:80])
print("tail:", p.read_text(encoding="utf-8").splitlines()[-1][:80])
