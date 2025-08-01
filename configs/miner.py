# miner.py
import os
import asyncio
import json
import re
import logging
from pathlib import Path
from telethon import TelegramClient
from dotenv import load_dotenv

# --- تنظیمات اولیه ---
# راه‌اندازی لاگینگ برای نمایش اطلاعات در ترمینال
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# خواندن اطلاعات از .env
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = 'telegram_session'

# بررسی وجود API_ID و API_HASH
if not API_ID or not API_HASH:
    raise ValueError("لطفاً API_ID و API_HASH را در فایل .env تنظیم کنید.")

# --- کانال‌ها و مسیرها ---
V2RAY_CHANNELS = ['@v2rayconfig', '@PrivateVPNs', '@FreeV2rays']
WIREGUARD_CHANNELS = ['@ConfigWireguard', '@WireGuardConfigs']

# مسیرهای ذخیره‌سازی
OUTPUT_DIR = Path("configs")
V2RAY_OUTPUT_FILE = OUTPUT_DIR / "v2ray" / "v2ray_subscription.txt"
WIREGUARD_OUTPUT_DIR = OUTPUT_DIR / "wireguard"

# --- عبارات باقاعده (Regex) ---
V2RAY_REGEX = r'(vmess|vless|trojan)://[^\s`"<]+'
WIREGUARD_BLOCK_REGEX = r'(\[Interface\][\s\S]*?\[Peer\][\s\S]*?Endpoint\s*=\s*.*)'
WIREGUARD_LINK_REGEX = r'wireguard://[^\s`"<]+'


async def process_v2ray_configs(client: TelegramClient):
    """کانفیگ‌های V2Ray را از کانال‌ها استخراج و در یک فایل ذخیره می‌کند."""
    logging.info("شروع استخراج کانفیگ‌های V2Ray...")
    
    # استفاده از set برای جلوگیری از ذخیره کانفیگ‌های تکراری
    unique_configs = set()

    for channel in V2RAY_CHANNELS:
        try:
            logging.info(f"در حال بررسی کانال: {channel}")
            async for message in client.iter_messages(channel, limit=200):
                if message.text:
                    found = re.findall(V2RAY_REGEX, message.text)
                    for config in found:
                        unique_configs.add(config)
        except Exception as e:
            logging.error(f"خطا در دسترسی به کانال {channel}: {e}")

    if not unique_configs:
        logging.warning("هیچ کانفیگ V2Ray پیدا نشد.")
        return

    # اطمینان از وجود پوشه مقصد
    V2RAY_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # ذخیره کانفیگ‌ها در فایل، هر کدام در یک خط
    with open(V2RAY_OUTPUT_FILE, "w", encoding="utf-8") as f:
        for config in unique_configs:
            f.write(f"{config}\n")

    logging.info(f"✅ V2Ray: {len(unique_configs)} کانفیگ منحصر به فرد در فایل زیر ذخیره شد:\n{V2RAY_OUTPUT_FILE}")


async def process_wireguard_configs(client: TelegramClient):
    """کانفیگ‌های WireGuard را استخراج و هر کدام را در یک فایل .conf جداگانه ذخیره می‌کند."""
    logging.info("شروع استخراج کانفیگ‌های WireGuard...")
    
    unique_configs = set()

    for channel in WIREGUARD_CHANNELS:
        try:
            logging.info(f"در حال بررسی کانال: {channel}")
            async for message in client.iter_messages(channel, limit=200):
                if not message.text:
                    continue
                
                # استخراج کانفیگ‌های متنی (بلوک کامل)
                text_blocks = re.findall(WIREGUARD_BLOCK_REGEX, message.text)
                for block in text_blocks:
                    unique_configs.add(block.strip())
                
                # استخراج کانفیگ از لینک‌ها
                links = re.findall(WIREGUARD_LINK_REGEX, message.text)
                for link in links:
                    try:
                        # تبدیل لینک به متن کانفیگ
                        config_str = " ".join(link.replace("wireguard://", "").split(","))
                        unique_configs.add(config_str)
                    except Exception as e:
                        logging.warning(f"خطا در پردازش لینک WireGuard: {e}")

        except Exception as e:
            logging.error(f"خطا در دسترسی به کانال {channel}: {e}")

    if not unique_configs:
        logging.warning("هیچ کانفیگ WireGuard پیدا نشد.")
        return

    # اطمینان از وجود پوشه مقصد
    WIREGUARD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # ذخیره هر کانفیگ در یک فایل جداگانه
    for i, config in enumerate(unique_configs):
        file_path = WIREGUARD_OUTPUT_DIR / f"wg_{i+1}.conf"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(config)

    logging.info(f"✅ WireGuard: {len(unique_configs)} کانفیگ منحصر به فرد در پوشه زیر ذخیره شد:\n{WIREGUARD_OUTPUT_DIR}")


async def main():
    """تابع اصلی برای اتصال به تلگرام و اجرای فرآیندها."""
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        logging.info("کلاینت تلگرام با موفقیت متصل شد.")
        await process_v2ray_configs(client)
        await process_wireguard_configs(client)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, TypeError) as e:
        logging.error(f"خطای ورودی: {e}")
    except Exception as e:
        logging.error(f"یک خطای پیش‌بینی نشده رخ داد: {e}")
    finally:
        logging.info("اسکریپت به پایان رسید.")
