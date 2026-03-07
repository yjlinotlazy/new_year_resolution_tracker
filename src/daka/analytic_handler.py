"""Analytics and summary handlers for daka."""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
import unicodedata

from daka.color_config import PALETTE, RESET
from daka.data_loader import load_data

BAR_WIDTH = 20
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _should_use_color() -> bool:
    if os.getenv("NO_COLOR") is not None:
        return False
    term = os.getenv("TERM", "")
    if term.lower() == "dumb":
        return False
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


def _resolution_color_map(data: dict) -> dict[str, str]:
    colors: dict[str, str] = {}
    next_idx = 0
    for resolution in data.get("resolutions", []):
        resolution_name = str(resolution.get("name", "")).strip()
        if not resolution_name or resolution_name in colors:
            continue
        colors[resolution_name] = PALETTE[next_idx % len(PALETTE)]
        next_idx += 1
    return colors


def summarize_all_checkins() -> None:
    data = load_data()
    use_color = _should_use_color()
    color_map = _resolution_color_map(data) if use_color else {}
    print("\n=== 全部打卡汇总 Summary ===")

    any_checkin = False
    for resolution in data.get("resolutions", []):
        resolution_name = str(resolution.get("name", "")).strip()
        if not resolution_name:
            continue

        for item in resolution.get("items", []):
            item_name = str(item.get("name", "")).strip()
            if not item_name:
                continue

            raw_checkins = item.get("checkins", [])
            if not isinstance(raw_checkins, list):
                continue

            checkins = sorted(set(str(c).strip() for c in raw_checkins if str(c).strip()))
            if not checkins:
                continue

            any_checkin = True
            display_resolution = resolution_name
            if use_color:
                color = color_map.get(resolution_name, "")
                display_resolution = f"{color}{resolution_name}{RESET}"
            print(f"{display_resolution} / {item_name}: {len(checkins)}")
            print("  " + ", ".join(checkins))

    if not any_checkin:
        print("(none)")


def _completion_bar(completion_percent: float) -> str:
    clamped = max(0.0, min(100.0, completion_percent))
    filled = int(round((clamped / 100.0) * BAR_WIDTH))
    return "[" + ("#" * filled) + ("-" * (BAR_WIDTH - filled)) + "]"


def _display_width(text: str) -> int:
    plain = ANSI_RE.sub("", text)
    width = 0
    for ch in plain:
        if unicodedata.combining(ch):
            continue
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def _pad_display(text: str, target_width: int) -> str:
    current = _display_width(text)
    if current >= target_width:
        return text
    return text + (" " * (target_width - current))


def summarize_completion() -> None:
    data = load_data()
    use_color = _should_use_color()
    color_map = _resolution_color_map(data) if use_color else {}
    year = dt.date.today().year
    days_in_year = 366 if dt.date(year, 12, 31).timetuple().tm_yday == 366 else 365
    total_weeks_in_year = (days_in_year + 6) // 7
    metrics: list[tuple[str, str, int, int]] = []
    for resolution in data.get("resolutions", []):
        resolution_name = str(resolution.get("name", "")).strip()
        if not resolution_name:
            continue

        for item in resolution.get("items", []):
            task_name = str(item.get("name", "")).strip()
            if not task_name:
                continue

            raw_checkins = item.get("checkins", [])
            if not isinstance(raw_checkins, list):
                continue

            valid_dates: set[dt.date] = set()
            for raw in raw_checkins:
                date_text = str(raw).strip()
                if not date_text:
                    continue
                try:
                    date_value = dt.date.fromisoformat(date_text)
                except ValueError:
                    continue
                if date_value.year == year:
                    valid_dates.add(date_value)

            checked_days = len(valid_dates)
            checked_weeks = len({((d.timetuple().tm_yday - 1) // 7) + 1 for d in valid_dates})
            display_resolution = resolution_name
            if use_color:
                color = color_map.get(resolution_name, "")
                display_resolution = f"{color}{resolution_name}{RESET}"

            metrics.append((display_resolution, task_name, checked_days, checked_weeks))

    if not metrics:
        print(f"\n=== Yearly Summary ({year}) ===")
        print("(none)")
        print(f"\n=== Weekly Summary ({year}) ===")
        print("(none)")
        return

    labels = [f"{display_resolution} / {task_name}" for display_resolution, task_name, _, _ in metrics]
    label_width = max(_display_width(label) for label in labels)
    day_ratio_width = len(f"{days_in_year}/{days_in_year}")
    week_ratio_width = len(f"{total_weeks_in_year}/{total_weeks_in_year}")
    percent_width = len("100.00%")

    print(f"\n=== Yearly Summary ({year}) ===")
    for (display_resolution, task_name, checked_days, _checked_weeks), label in zip(metrics, labels):
        day_completion = (checked_days / days_in_year) * 100
        day_bar = _completion_bar(day_completion)
        ratio = f"{checked_days}/{days_in_year}"
        percent = f"{day_completion:.2f}%"
        print(
            f"{_pad_display(label, label_width)} : "
            f"{ratio:>{day_ratio_width}}  "
            f"{percent:>{percent_width}}  "
            f"{day_bar}"
        )

    print(f"\n=== Weekly Summary ({year}) ===")
    for (display_resolution, task_name, _checked_days, checked_weeks), label in zip(metrics, labels):
        week_completion = (checked_weeks / total_weeks_in_year) * 100
        week_bar = _completion_bar(week_completion)
        ratio = f"{checked_weeks}/{total_weeks_in_year}"
        percent = f"{week_completion:.2f}%"
        print(
            f"{_pad_display(label, label_width)} : "
            f"{ratio:>{week_ratio_width}}  "
            f"{percent:>{percent_width}}  "
            f"{week_bar}"
        )
