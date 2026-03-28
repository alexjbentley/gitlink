import sys

from gitlink import accept, check


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: git-link <subcommand>", file=sys.stderr)
        sys.exit(1)

    subcommand = sys.argv[1]

    if subcommand == "check":
        check.run()
    elif subcommand == "accept":
        accept.run()
    else:
        print(f"unknown subcommand: {subcommand}", file=sys.stderr)
        sys.exit(1)
