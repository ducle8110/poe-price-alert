"""Fetch dữ liệu giá từ poe.ninja API."""

import time
import requests
from config import POE_NINJA_BASE, LEAGUE, CURRENCY_TYPES, ITEM_TYPES


def fetch_currency(currency_type: str) -> list[dict]:
    """Lấy dữ liệu currency từ poe.ninja."""
    url = f"{POE_NINJA_BASE}/currencyoverview"
    params = {"league": LEAGUE, "type": currency_type}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for line in data.get("lines", []):
        items.append({
            "name": line["currencyTypeName"],
            "type": currency_type,
            "chaos_value": line.get("chaosEquivalent", 0),
            "change_7d": line.get("receiveSparkLine", {}).get("totalChange", 0),
            "details_id": line.get("detailsId", ""),
            "listing_count": line.get("receive", {}).get("listing_count", 0),
        })
    return items


def fetch_items(item_type: str) -> list[dict]:
    """Lấy dữ liệu item từ poe.ninja."""
    url = f"{POE_NINJA_BASE}/itemoverview"
    params = {"league": LEAGUE, "type": item_type}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for line in data.get("lines", []):
        items.append({
            "name": line["name"],
            "type": item_type,
            "chaos_value": line.get("chaosValue", 0),
            "change_7d": line.get("sparkLine", {}).get("totalChange", 0),
            "details_id": line.get("detailsId", ""),
            "listing_count": line.get("listingCount", 0),
            "links": line.get("links", 0),
            "base_type": line.get("baseType", ""),
        })
    return items


def fetch_all() -> dict[str, dict]:
    """Lấy toàn bộ dữ liệu, trả về dict {item_key: item_data}."""
    all_items = {}

    for ct in CURRENCY_TYPES:
        try:
            items = fetch_currency(ct)
            for item in items:
                key = f"{ct}::{item['name']}"
                all_items[key] = item
            print(f"  [OK] {ct}: {len(items)} items")
        except Exception as e:
            print(f"  [ERR] {ct}: {e}")
        time.sleep(1)  # tránh spam API

    for it in ITEM_TYPES:
        try:
            items = fetch_items(it)
            for item in items:
                key = f"{it}::{item['name']}"
                # Nếu item có links (6L), thêm vào key để phân biệt
                if item.get("links", 0) > 0:
                    key += f"::L{item['links']}"
                all_items[key] = item
            print(f"  [OK] {it}: {len(items)} items")
        except Exception as e:
            print(f"  [ERR] {it}: {e}")
        time.sleep(1)

    return all_items
