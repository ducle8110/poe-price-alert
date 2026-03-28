# PoE Price Alert Bot

Theo dõi giá item trên [poe.ninja](https://poe.ninja), gửi alert Discord khi phát hiện biến động giá mạnh.

## Tính năng

- Theo dõi tất cả loại item: Currency, Unique, Divination Card, Gem, Scarab, Fossil...
- So sánh giá giữa các lần poll để phát hiện biến động
- Gửi alert đến Discord qua webhook với link đến poe.ninja và trade site
- Cấu hình ngưỡng alert, giá tối thiểu, poll interval qua `.env`

## Cài đặt

```bash
pip install -r requirements.txt
cp .env.example .env
# Sửa .env với Discord Webhook URL của bạn
```

## Tạo Discord Webhook

1. Vào Discord Server > Settings > Integrations > Webhooks
2. Tạo webhook mới, copy URL
3. Paste vào `DISCORD_WEBHOOK_URL` trong file `.env`

## Chạy

```bash
python main.py
```

## Cấu hình (.env)

| Biến | Mô tả | Mặc định |
|------|--------|----------|
| `DISCORD_WEBHOOK_URL` | URL webhook Discord | (bắt buộc) |
| `LEAGUE` | League theo dõi | Standard |
| `PRICE_CHANGE_THRESHOLD` | Ngưỡng biến động (%) | 15 |
| `MIN_CHAOS_VALUE` | Giá tối thiểu (chaos) ~10 divine | 700 |
| `POLL_INTERVAL` | Thời gian giữa mỗi lần check (giây) | 300 |
