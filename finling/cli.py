"""CLI entry point for FinLing."""
from __future__ import annotations

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="finling",
        description="FinLing — Financial intelligence in African languages",
    )
    subparsers = parser.add_subparsers(dest="command")

    # finling query "Wo ho te sɛn?" --lang tw
    q = subparsers.add_parser("query", help="Ask a financial question")
    q.add_argument("text", help="Your question")
    q.add_argument("--lang", dest="lang_code", default=None, help="Language code e.g. tw")

    # finling languages
    subparsers.add_parser("languages", help="List supported languages")

    args = parser.parse_args()

    if args.command == "query":
        from finling.pipeline.core import FinLingPipeline
        pipeline = FinLingPipeline()
        result = pipeline.query(args.text, args.lang_code)
        print(f"\n[{result.detected_language}] {result.original_query}")
        print(f"\nResponse ({result.detected_language}):\n{result.response_local}")
        print(f"\nResponse (en):\n{result.response_en}")

    elif args.command == "languages":
        from finling.languages.registry import supported_languages
        langs = supported_languages()
        print(json.dumps([{"code": l.code, "name": l.name} for l in langs], indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
