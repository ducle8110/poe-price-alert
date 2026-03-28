"""Gửi alert đến Discord qua webhook."""

import requests
from config import DISCORD_WEBHOOK_URL, LEAGUE

# Màu embed theo loại biến động
COLOR_PRICE_DROP = 0xFF4444    # đỏ - giảm giá
COLOR_PRICE_SPIKE = 0x44FF44   # xanh - tăng giá


def make_trade_url(item_name: str, item_type: str) -> str:
    """Tạo link trade search trên pathofexile.com."""
    # Link tổng quát - user sẽ tự search
    base = f"https://www.pathofexile.com/trade/search/{LEAGUE}"
    return base


def make_ninja_url(details_id: str, item_type: str) -> str:
    """Tạo link poe.ninja cho item."""
    # Currency types dùng /currency/, item types dùng tên type lowercase
    currency_types = {"Currency", "Fragment"}
    if item_type in currency_types:
        return f"https://poe.ninja/economy/{LEAGUE.lower()}/currency/{details_id}"

    type_map = {
        "UniqueWeapon": "unique-weapons",
        "UniqueArmour": "unique-armours",
        "UniqueAccessory": "unique-accessories",
        "UniqueFlask": "unique-flasks",
        "UniqueJewel": "unique-jewels",
        "UniqueRelic": "unique-relics",
        "SkillGem": "skill-gems",
        "BaseType": "base-types",
        "DivinationCard": "divination-cards",
        "Artifact": "artifacts",
        "Oil": "oils",
        "Incubator": "incubators",
        "Scarab": "scarabs",
        "Fossil": "fossils",
        "Resonator": "resonators",
        "Essence": "essences",
        "DeliriumOrb": "delirium-orbs",
        "Invitation": "invitations",
        "ClusterJewel": "cluster-jewels",
        "Memory": "memories",
    }
    slug = type_map.get(item_type, item_type.lower())
    return f"https://poe.ninja/economy/{LEAGUE.lower()}/{slug}/{details_id}"


def send_alert(alerts: list[dict]):
    """Gửi batch alert đến Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("[WARN] DISCORD_WEBHOOK_URL chưa được cấu hình!")
        return

    # Discord cho phép tối đa 10 embeds / message
    for i in range(0, len(alerts), 10):
        batch = alerts[i:i + 10]
        embeds = []

        for alert in batch:
            is_drop = alert["change_pct"] < 0
            color = COLOR_PRICE_DROP if is_drop else COLOR_PRICE_SPIKE
            direction = "GIẢM" if is_drop else "TĂNG"
            emoji = "📉" if is_drop else "📈"

            ninja_url = make_ninja_url(alert["details_id"], alert["type"])
            trade_url = make_trade_url(alert["name"], alert["type"])

            embed = {
                "title": f"{emoji} {alert['name']} — {direction} {abs(alert['change_pct']):.1f}%",
                "color": color,
                "fields": [
                    {
                        "name": "Giá hiện tại",
                        "value": f"**{alert['current_price']:.1f}** chaos",
                        "inline": True,
                    },
                    {
                        "name": "Giá trước",
                        "value": f"{alert['old_price']:.1f} chaos",
                        "inline": True,
                    },
                    {
                        "name": "Loại",
                        "value": alert["type"],
                        "inline": True,
                    },
                    {
                        "name": "Links",
                        "value": f"[poe.ninja]({ninja_url}) | [Trade]({trade_url})",
                        "inline": False,
                    },
                ],
            }
            embeds.append(embed)

        payload = {
            "username": "PoE Price Alert",
            "embeds": embeds,
        }

        try:
            resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
            resp.raise_for_status()
            print(f"  [Discord] Đã gửi {len(batch)} alerts")
        except Exception as e:
            print(f"  [Discord ERR] {e}")
