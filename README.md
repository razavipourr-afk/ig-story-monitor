# IG Story Monitor

این پروژه هر ۱۰ تا ۲۰ دقیقه با GitHub Actions اجرا می‌شود، استوری‌های جدید پیج‌های مشخص‌شده را بررسی می‌کند و عکس/ویدئو و لینک احتمالی داخل استوری را به تلگرام می‌فرستد.

## Secrets لازم در GitHub

در مسیر زیر اضافه کنید:

Settings → Secrets and variables → Actions → New repository secret

- `IG_USERNAME`
- `IG_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## تغییر پیج‌ها

داخل فایل `config.py` لیست `TARGET_PROFILES` را تغییر دهید.

## اجرای دستی

از تب Actions روی `IG Story Monitor` بروید و `Run workflow` را بزنید.
