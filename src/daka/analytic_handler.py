"""Analytics and summary handlers for daka."""

from __future__ import annotations

import os
import sys

from daka.color_config import PALETTE, RESET
from daka.data_loader import load_data


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
