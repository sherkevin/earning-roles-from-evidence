from pathlib import Path


REQUIRED_DIRS = [
    "artifacts/round0",
    "artifacts/round1",
    "artifacts/round2",
    "prompts",
    "configs",
    "scripts",
    "workspace",
]


def main() -> None:
    for rel in REQUIRED_DIRS:
        Path(rel).mkdir(parents=True, exist_ok=True)
    print("Bootstrap directories verified.")


if __name__ == "__main__":
    main()
