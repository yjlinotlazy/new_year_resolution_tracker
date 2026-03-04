"""Core handler logic for daka."""

from __future__ import annotations

import datetime as dt
from typing import Any

from daka.data_loader import load_data, save_checkins, save_resolutions


def parse_date(date_text: str | None) -> str:
    if not date_text:
        return dt.date.today().isoformat()
    try:
        return dt.date.fromisoformat(date_text).isoformat()
    except ValueError as e:
        raise SystemExit(f"Invalid date: {date_text}. Use YYYY-MM-DD.") from e


def display_menu(title: str, entries: list[str]) -> None:
    print(f"\n{title}")
    if not entries:
        print("(none)")
    for i, entry in enumerate(entries, start=1):
        print(f"{i}. {entry}")
    print("输入数字=选择，输入文字=新增，直接回车=返回，输入 q=退出")


def ask_choice(entries: list[str], add_prompt: str) -> tuple[str, int | str | None]:
    raw = input(f"{add_prompt}: ").strip()

    if raw == "":
        return ("back", None)
    if raw.lower() == "q":
        return ("quit", None)

    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(entries):
            return ("select", idx)
        print("数字超出范围，请重试。")
        return ("retry", None)

    return ("add", raw)


def ensure_resolution(data: dict[str, Any], name: str) -> int:
    res = {"name": name, "items": []}
    data["resolutions"].append(res)
    return len(data["resolutions"]) - 1


def ensure_item(resolution: dict[str, Any], item_name: str) -> int:
    item = {"name": item_name, "checkins": []}
    resolution["items"].append(item)
    return len(resolution["items"]) - 1


def check_in(item: dict[str, Any], date_str: str) -> bool:
    checkins = item.get("checkins")
    if not isinstance(checkins, list):
        checkins = []
        item["checkins"] = checkins

    if date_str in checkins:
        return False

    checkins.append(date_str)
    checkins.sort()
    return True


def run(date_str: str) -> None:
    data = load_data()

    while True:
        resolutions = data["resolutions"]
        display_menu("=== 选择打卡项目 Resolution ===", [r["name"] for r in resolutions])
        action, value = ask_choice(resolutions, "选择或新增项目")

        if action == "back":
            print("已退出。")
            break
        if action == "quit":
            print("已退出。")
            return
        if action == "retry":
            continue
        if action == "add":
            selected_resolution_idx = ensure_resolution(data, str(value))
            save_resolutions(data)
            print(f"已新增项目: {value}")
        else:
            selected_resolution_idx = int(value)

        resolution = resolutions[selected_resolution_idx]

        while True:
            items = resolution["items"]
            display_menu(
                f"=== {resolution['name']} / 选择具体条目 Item ===",
                [i["name"] for i in items],
            )
            action2, value2 = ask_choice(items, "选择或新增条目")

            if action2 == "back":
                break
            if action2 == "quit":
                print("已退出。")
                return
            if action2 == "retry":
                continue
            if action2 == "add":
                selected_item_idx = ensure_item(resolution, str(value2))
                save_resolutions(data)
                print(f"已新增条目: {value2}")
            else:
                selected_item_idx = int(value2)

            item = items[selected_item_idx]
            done = check_in(item, date_str)
            if done:
                save_checkins(data)

            if done:
                print(f"打卡成功: {resolution['name']} / {item['name']} @ {date_str}")
            else:
                print(f"今天已打卡: {resolution['name']} / {item['name']} @ {date_str}")
