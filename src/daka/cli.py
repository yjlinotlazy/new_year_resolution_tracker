"""CLI entry point for daka."""

from __future__ import annotations

import argparse

from daka.analytic_handler import summarize_all_checkins
from daka.handler import parse_date, rename_entities, run


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple new year resolution tracker daka")
    parser.add_argument("-d", "--date", help="check-in date in YYYY-MM-DD (default: today)")
    parser.add_argument("-s", "--summary", action="store_true", help="summarize all check-ins and exit")
    parser.add_argument("--rename", action="store_true", help="rename a resolution or item and exit")
    args = parser.parse_args()

    if args.summary:
        summarize_all_checkins()
        return
    if args.rename:
        rename_entities()
        return

    date_str = parse_date(args.date)
    run(date_str)


if __name__ == "__main__":
    main()
