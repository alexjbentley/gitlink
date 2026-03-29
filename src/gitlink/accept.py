import subprocess
import sys
from pathlib import Path

from gitlink._git import repo_root

SIDECAR = ".gitlink-accept"


def read_accepts(root: Path) -> dict[str, str]:
    """Return a mapping of accepted link names to their reasons."""
    sidecar = root / SIDECAR
    if not sidecar.exists():
        return {}
    accepts = {}
    for line in sidecar.read_text().splitlines():
        if line.strip():
            parts = line.split(None, 1)
            accepts[parts[0]] = parts[1] if len(parts) > 1 else ""
    return accepts


def run() -> None:
    args = sys.argv[2:]  # strip "git-link accept"
    if len(args) < 2:
        print("usage: git-link accept <name> <reason>", file=sys.stderr)
        sys.exit(2)

    name = args[0]
    reason = " ".join(args[1:])

    root = repo_root()
    sidecar = root / SIDECAR

    with sidecar.open("a") as f:
        f.write(f"{name} {reason}\n")

    subprocess.run(["git", "add", str(sidecar)], check=True)
