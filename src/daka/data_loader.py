"""Persistence helpers for daka."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path("~/.config/daka").expanduser()
RESOLUTIONS_FILE = CONFIG_DIR / "resolutions.json"
DATA_FILE = CONFIG_DIR / "data.csv"


def load_data() -> dict[str, Any]:
    data = load_resolutions()
    load_checkins(data)
    return data


def load_resolutions() -> dict[str, Any]:
    if not RESOLUTIONS_FILE.exists():
        return {"resolutions": []}

    try:
        with RESOLUTIONS_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"resolutions": []}

    if not isinstance(raw, dict):
        return {"resolutions": []}

    resolutions_raw = raw.get("resolutions")
    if not isinstance(resolutions_raw, list):
        return {"resolutions": []}

    resolutions: list[dict[str, Any]] = []
    for r in resolutions_raw:
        if not isinstance(r, dict):
            continue
        name = str(r.get("name", "")).strip()
        if not name:
            continue
        items_raw = r.get("items")
        if not isinstance(items_raw, list):
            items_raw = []

        items: list[dict[str, Any]] = []
        for i in items_raw:
            if not isinstance(i, dict):
                continue
            item_name = str(i.get("name", "")).strip()
            if not item_name:
                continue
            items.append({"name": item_name, "checkins": []})

        resolutions.append({"name": name, "items": items})

    return {"resolutions": resolutions}


def load_checkins(data: dict[str, Any]) -> None:
    if not DATA_FILE.exists():
        return

    resolution_map: dict[str, dict[str, Any]] = {r["name"]: r for r in data["resolutions"]}

    try:
        with DATA_FILE.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                resolution_name = (row.get("resolution") or "").strip()
                item_name = (row.get("item") or "").strip()
                date_str = (row.get("date") or "").strip()

                if not resolution_name or not item_name or not date_str:
                    continue

                resolution = resolution_map.get(resolution_name)
                if resolution is None:
                    resolution = {"name": resolution_name, "items": []}
                    data["resolutions"].append(resolution)
                    resolution_map[resolution_name] = resolution

                item = next((i for i in resolution["items"] if i["name"] == item_name), None)
                if item is None:
                    item = {"name": item_name, "checkins": []}
                    resolution["items"].append(item)

                if date_str not in item["checkins"]:
                    item["checkins"].append(date_str)
    except OSError:
        return

    for resolution in data["resolutions"]:
        for item in resolution["items"]:
            item["checkins"].sort()


def save_resolutions(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    payload = {"resolutions": []}
    for resolution in data.get("resolutions", []):
        resolution_name = str(resolution.get("name", "")).strip()
        if not resolution_name:
            continue

        items_payload = []
        for item in resolution.get("items", []):
            item_name = str(item.get("name", "")).strip()
            if item_name:
                items_payload.append({"name": item_name})

        payload["resolutions"].append({"name": resolution_name, "items": items_payload})

    with RESOLUTIONS_FILE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def save_checkins(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["resolution", "item", "date"])

        for resolution in data.get("resolutions", []):
            resolution_name = str(resolution.get("name", "")).strip()
            if not resolution_name:
                continue

            for item in resolution.get("items", []):
                item_name = str(item.get("name", "")).strip()
                if not item_name:
                    continue
                checkins = item.get("checkins", [])
                for date_str in sorted(set(str(c).strip() for c in checkins if c)):
                    writer.writerow([resolution_name, item_name, date_str])

