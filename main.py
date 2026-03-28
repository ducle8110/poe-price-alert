"""
PoE Price Alert Bot
Theo dõi giá item trên poe.ninja, alert Discord khi biến động mạnh.
"""

import json
import time
from datetime import datetime

from config import PRICE_CHANGE_THRESHOLD, MIN_CHAOS_VALUE, POLL_INTERVAL, CACHE_FILE
from poe_ninja import fetch_all
from discord_notify import send_alert


def load_cache() -> dict:
    """Load giá cũ từ cache file."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(data: dict):
    """Lưu giá hiện tại vào cache."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def detect_alerts(old_data: dict, new_data: dict) -> list[dict]:
    """So sánh giá cũ vs mới, tìm item biến động mạnh."""
    alerts = []

    for key, new_item in new_data.items():
        current_price = new_item["chaos_value"]

        # Bỏ qua item giá quá thấp
        if current_price < MIN_CHAOS_VALUE:
            continue

        # Nếu chưa có dữ liệu cũ, dùng sparkLine 7-day change
        if key not in old_data:
            change_7d = new_item.get("change_7d", 0) or 0
            if abs(change_7d) >= PRICE_CHANGE_THRESHOLD:
                alerts.append({
                    "name": new_item["name"],
                    "type": new_item["type"],
                    "current_price": current_price,
                    "old_price": current_price / (1 + change_7d / 100) if change_7d != -100 else 0,
                    "change_pct": change_7d,
                    "details_id": new_item.get("details_id", ""),
                    "source": "7d_sparkline",
                })
            continue

        old_price = old_data[key].get("chaos_value", 0)
        if old_price <= 0:
            continue

        change_pct = ((current_price - old_price) / old_price) * 100

        if abs(change_pct) >= PRICE_CHANGE_THRESHOLD:
            alerts.append({
                "name": new_item["name"],
                "type": new_item["type"],
                "current_price": current_price,
                "old_price": old_price,
                "change_pct": change_pct,
                "details_id": new_item.get("details_id", ""),
                "source": "price_compare",
            })

    # Sắp xếp theo mức biến động mạnh nhất
    alerts.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return alerts


def run_once():
    """Chạy 1 lần: fetch, so sánh, alert."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*50}")
    print(f"[{now}] Đang fetch dữ liệu từ poe.ninja...")

    old_data = load_cache()
    new_data = fetch_all()

    if not new_data:
        print("[ERR] Không fetch được dữ liệu!")
        return

    print(f"\nTổng: {len(new_data)} items")
    print(f"Cache cũ: {len(old_data)} items")

    alerts = detect_alerts(old_data, new_data)

    if alerts:
        print(f"\n🔔 Phát hiện {len(alerts)} item biến động > {PRICE_CHANGE_THRESHOLD}%:")
        for a in alerts[:20]:  # hiển thị top 20
            direction = "📉" if a["change_pct"] < 0 else "📈"
            print(f"  {direction} {a['name']} ({a['type']}): "
                  f"{a['old_price']:.1f} → {a['current_price']:.1f} chaos "
                  f"({a['change_pct']:+.1f}%)")

        send_alert(alerts[:20])  # gửi top 20 alerts
    else:
        print("\n✅ Không có biến động lớn.")

    # Lưu cache cho lần sau
    # Chỉ lưu các field cần thiết
    cache_data = {}
    for key, item in new_data.items():
        cache_data[key] = {
            "chaos_value": item["chaos_value"],
            "name": item["name"],
            "type": item["type"],
        }
    save_cache(cache_data)


def main():
    """Main loop - chạy liên tục."""
    print("=" * 50)
    print("  PoE Price Alert Bot")
    print(f"  League: Standard")
    print(f"  Ngưỡng alert: {PRICE_CHANGE_THRESHOLD}%")
    print(f"  Giá tối thiểu: {MIN_CHAOS_VALUE} chaos")
    print(f"  Poll interval: {POLL_INTERVAL}s")
    print("=" * 50)

    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            print("\n[EXIT] Đã dừng bot.")
            break
        except Exception as e:
            print(f"\n[ERR] Lỗi không mong đợi: {e}")

        print(f"\n⏳ Chờ {POLL_INTERVAL}s...")
        try:
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\n[EXIT] Đã dừng bot.")
            break


if __name__ == "__main__":
    main()
