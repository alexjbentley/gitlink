import sys

from gitlink import accept, add, check


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: git-link <subcommand>", file=sys.stderr)
        sys.exit(1)

    subcommand = sys.argv[1]

    match subcommand:
        case "accept":
            accept.run()
        case "add":
            add.run()
        case "check":
            check.run()
        case _:
            print(f"unknown subcommand: {subcommand}", file=sys.stderr)
            sys.exit(1)
