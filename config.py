import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
LEAGUE = os.getenv("LEAGUE", "Standard")
PRICE_CHANGE_THRESHOLD = float(os.getenv("PRICE_CHANGE_THRESHOLD", "15"))
MIN_CHAOS_VALUE = float(os.getenv("MIN_CHAOS_VALUE", "700"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))

# Tất cả item types trên poe.ninja
# Currency dùng endpoint khác (currencyoverview), còn lại dùng itemoverview
CURRENCY_TYPES = []

# Chỉ theo dõi Unique items
ITEM_TYPES = [
    "UniqueWeapon",
    "UniqueArmour",
    "UniqueAccessory",
    "UniqueFlask",
    "UniqueJewel",
    "UniqueRelic",
]

POE_NINJA_BASE = "https://poe.ninja/api/data"
CACHE_FILE = "price_cache.json"
