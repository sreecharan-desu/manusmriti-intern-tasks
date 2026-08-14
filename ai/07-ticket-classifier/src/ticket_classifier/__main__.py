from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from ticket_classifier.classify import classify


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Classify a customer support message")
    parser.add_argument("message", nargs="*")
    parser.add_argument("--no-offline", action="store_true")
    args = parser.parse_args(argv)
    message = " ".join(args.message).strip()
    if not message:
        parser.error("Provide a customer message")
    try:
        result = classify(message, allow_offline=not args.no_offline)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
