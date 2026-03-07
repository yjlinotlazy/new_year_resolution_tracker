"""CLI entry point for daka."""

from __future__ import annotations

import argparse

from daka.analytic_handler import summarize_all_checkins, summarize_completion
from daka.handler import parse_date, rename_entities, run


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple new year resolution tracker: 打卡")
    parser.add_argument("-d", "--date", help="check-in date in YYYY-MM-DD (default: today)")
    parser.add_argument("-l", "--log", action="store_true", help="show raw check-in log")
    parser.add_argument("-s", "--summary", action="store_true", help="show yearly completion percentages")
    parser.add_argument("--rename", action="store_true", help="rename a resolution or task")
    args = parser.parse_args()

    if args.log:
        summarize_all_checkins()
        return
    if args.summary:
        summarize_completion()
        return
    if args.rename:
        rename_entities()
        return

    # Otherwise run regular mode to checkin
    date_str = parse_date(args.date)
    run(date_str)


if __name__ == "__main__":
    main()
