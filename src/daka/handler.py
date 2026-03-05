"""Core handler logic for daka."""

from __future__ import annotations

import datetime as dt
import os
import sys
from typing import Any

from daka.color_config import PALETTE, RESET
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


def display_select_menu(title: str, entries: list[str]) -> None:
    print(f"\n{title}")
    if not entries:
        print("(none)")
    for i, entry in enumerate(entries, start=1):
        print(f"{i}. {entry}")
    print("输入数字=选择，直接回车=返回，输入 q=退出")


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


def _should_use_color() -> bool:
    if os.getenv("NO_COLOR") is not None:
        return False
    term = os.getenv("TERM", "")
    if term.lower() == "dumb":
        return False
    return bool(getattr(sys.stdout, "isatty", lambda: False)())


def _resolution_color_map(resolutions: list[dict[str, Any]]) -> dict[str, str]:
    colors: dict[str, str] = {}
    next_idx = 0
    for resolution in resolutions:
        resolution_name = str(resolution.get("name", "")).strip()
        if not resolution_name or resolution_name in colors:
            continue
        colors[resolution_name] = PALETTE[next_idx % len(PALETTE)]
        next_idx += 1
    return colors


def _format_resolution_name(resolution_name: str, use_color: bool, color_map: dict[str, str]) -> str:
    if not use_color:
        return resolution_name
    color = color_map.get(resolution_name, "")
    if not color:
        return resolution_name
    return f"{color}{resolution_name}{RESET}"


def _ask_index(entries: list[str], prompt: str) -> tuple[str, int | None]:
    raw = input(f"{prompt}: ").strip()
    if raw == "":
        return ("back", None)
    if raw.lower() == "q":
        return ("quit", None)
    if not raw.isdigit():
        print("请输入数字。")
        return ("retry", None)

    idx = int(raw) - 1
    if not 0 <= idx < len(entries):
        print("数字超出范围，请重试。")
        return ("retry", None)

    return ("select", idx)


def _rename_resolution(data: dict[str, Any], idx: int) -> bool:
    resolutions = data["resolutions"]
    current_name = str(resolutions[idx]["name"]).strip()
    new_name = input(f"新的 Resolution 名称（当前: {current_name}）: ").strip()
    if not new_name:
        print("名称不能为空。")
        return False

    existing = {str(r.get("name", "")).strip() for i, r in enumerate(resolutions) if i != idx}
    if new_name in existing:
        print("名称已存在，请使用其他名称。")
        return False

    resolutions[idx]["name"] = new_name
    save_resolutions(data)
    save_checkins(data)
    print(f"已重命名 Resolution: {current_name} -> {new_name}")
    return True


def _rename_item(data: dict[str, Any], resolution_idx: int) -> bool:
    resolution = data["resolutions"][resolution_idx]
    items = resolution["items"]
    if not items:
        print("该 Resolution 下没有 Item。")
        return False

    display_select_menu(
        f"=== {resolution['name']} / 选择要重命名的 Item ===",
        [str(i["name"]) for i in items],
    )
    action, item_idx = _ask_index([str(i["name"]) for i in items], "输入数字选择 Item，回车返回，q退出")
    if action == "back":
        return False
    if action == "quit":
        raise SystemExit("已退出。")
    if action == "retry":
        return False

    assert item_idx is not None
    current_name = str(items[item_idx]["name"]).strip()
    new_name = input(f"新的 Item 名称（当前: {current_name}）: ").strip()
    if not new_name:
        print("名称不能为空。")
        return False

    existing = {str(i.get("name", "")).strip() for i_idx, i in enumerate(items) if i_idx != item_idx}
    if new_name in existing:
        print("名称已存在，请使用其他名称。")
        return False

    items[item_idx]["name"] = new_name
    save_resolutions(data)
    save_checkins(data)
    print(f"已重命名 Item: {current_name} -> {new_name}")
    return True


def rename_entities() -> None:
    data = load_data()
    use_color = _should_use_color()

    while True:
        resolutions = data["resolutions"]
        color_map = _resolution_color_map(resolutions) if use_color else {}
        display_select_menu(
            "=== 选择要重命名的 Resolution ===",
            [_format_resolution_name(str(r["name"]), use_color, color_map) for r in resolutions],
        )
        action, resolution_idx = _ask_index(resolutions, "输入数字选择 Resolution，回车返回，q退出")

        if action == "back":
            print("已退出。")
            return
        if action == "quit":
            print("已退出。")
            return
        if action == "retry":
            continue

        assert resolution_idx is not None
        resolution = resolutions[resolution_idx]
        command = input("输入 r 重命名 Resolution，输入 i 重命名 Item，回车返回，q退出: ").strip().lower()

        if command == "":
            continue
        if command == "q":
            print("已退出。")
            return
        if command == "r":
            _rename_resolution(data, resolution_idx)
            continue
        if command == "i":
            try:
                _rename_item(data, resolution_idx)
            except SystemExit as e:
                print(e)
                return
            continue

        print("无效输入，请输入 r / i / q。")


def run(date_str: str) -> None:
    data = load_data()
    use_color = _should_use_color()

    while True:
        resolutions = data["resolutions"]
        color_map = _resolution_color_map(resolutions) if use_color else {}
        resolution_entries = [
            _format_resolution_name(str(r["name"]), use_color, color_map) for r in resolutions
        ]
        display_menu("=== 选择打卡项目 Resolution ===", resolution_entries)
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
        resolution_display_name = _format_resolution_name(
            str(resolution["name"]),
            use_color,
            color_map,
        )

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
                print(f"打卡成功: {resolution_display_name} / {item['name']} @ {date_str}")
            else:
                print(f"今天已打卡: {resolution_display_name} / {item['name']} @ {date_str}")
