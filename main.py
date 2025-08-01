# main.py
import os
import shutil
import logging
import asyncio
from pathlib import Path
from zipfile import ZipFile
from flask import Flask, send_from_directory, jsonify
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# وارد کردن تابع اصلی از اسکریپت ماینر
import configs.miner

# --- تنظیمات اولیه ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- مسیرها ---
ROOT_DIR = Path(__file__).parent
CONFIGS_DIR = ROOT_DIR / "configs"
DOWNLOADS_DIR = ROOT_DIR / "downloads"
WIREGUARD_CONFIG_DIR = CONFIGS_DIR / "wireguard"
V2RAY_SUB_FILE = CONFIGS_DIR / "v2ray" / "v2ray_subscription.txt"
WIREGUARD_ZIP_NAME = "wireguard_configs.zip"
WIREGUARD_ZIP_PATH = DOWNLOADS_DIR / WIREGUARD_ZIP_NAME

# --- راه‌اندازی Flask ---
app = Flask(__name__)

def cleanup_old_files():
    """فایل‌های کانفیگ و zip قدیمی را پاک می‌کند."""
    logging.info("در حال پاکسازی فایل‌های قدیمی...")
    if CONFIGS_DIR.exists():
        shutil.rmtree(CONFIGS_DIR)
        logging.info(f"پوشه {CONFIGS_DIR} پاک شد.")
    if DOWNLOADS_DIR.exists():
        shutil.rmtree(DOWNLOADS_DIR)
        logging.info(f"پوشه {DOWNLOADS_DIR} پاک شد.")
    # ساخت مجدد پوشه‌ها
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    CONFIGS_DIR.mkdir(exist_ok=True)

def zip_wireguard_configs():
    """فایل‌های .conf مربوط به WireGuard را فشرده می‌کند."""
    if not WIREGUARD_CONFIG_DIR.is_dir() or not any(WIREGUARD_CONFIG_DIR.iterdir()):
        logging.warning("هیچ کانفیگ WireGuard برای فشرده‌سازی یافت نشد.")
        return False

    logging.info(f"در حال ساخت فایل zip در مسیر: {WIREGUARD_ZIP_PATH}")
    with ZipFile(WIREGUARD_ZIP_PATH, 'w') as zipf:
        for file_path in WIREGUARD_CONFIG_DIR.glob('*.conf'):
            zipf.write(file_path, arcname=file_path.name)
    
    logging.info(f"فایل {WIREGUARD_ZIP_NAME} با موفقیت ساخته شد.")
    return True

async def daily_update_task():
    """وظیفه اصلی که به صورت روزانه اجرا می‌شود."""
    logging.info("--- شروع وظیفه به‌روزرسانی روزانه ---")
    
    # ۱. پاکسازی فایل‌های قدیمی
    cleanup_old_files()
    
    # ۲. اجرای ماینر برای دریافت کانفیگ‌های جدید
    try:
        await miner.main()
    except Exception as e:
        logging.error(f"خطا در اجرای miner.py: {e}")
        return

    # ۳. فشرده‌سازی کانفیگ‌های جدید WireGuard
    zip_wireguard_configs()
    
    logging.info("--- وظیفه به‌روزرسانی روزانه با موفقیت به پایان رسید ---")

# --- تعریف API Endpoints ---
@app.route('/')
def index():
    """صفحه اصلی که لینک‌های دانلود را نمایش می‌دهد."""
    return jsonify({
        "project": "OxygenNet",
        "description": "Free Internet Access Configurations",
        "downloads": {
            "v2ray_subscription": "/subscription/v2ray",
            "wireguard_zip": "/download/wireguard"
        }
    })

@app.route('/download/wireguard')
def download_wireguard_zip():
    """لینک دانلود فایل zip کانفیگ‌های WireGuard."""
    if not WIREGUARD_ZIP_PATH.exists():
        return jsonify({"error": "File not found. The update task may be running."}), 404
    return send_from_directory(DOWNLOADS_DIR, WIREGUARD_ZIP_NAME, as_attachment=True)

@app.route('/subscription/v2ray')
def download_v2ray_subscription():
    """لینک سابسکریپشن برای V2Ray."""
    if not V2RAY_SUB_FILE.exists():
        return jsonify({"error": "File not found. The update task may be running."}), 404
    return send_from_directory(V2RAY_SUB_FILE.parent, V2RAY_SUB_FILE.name, as_attachment=False, mimetype='text/plain')

async def main():
    # اجرای وظیفه برای اولین بار هنگام شروع برنامه
    await daily_update_task()

    # تنظیم زمان‌بندی برای اجرای روزانه
    scheduler = AsyncIOScheduler()
    # وظیفه را هر روز ساعت ۳ بامداد اجرا می‌کند
    scheduler.add_job(daily_update_task, 'cron', hour=3, minute=0)
    scheduler.start()
    
    logging.info("زمان‌بند (Scheduler) برای به‌روزرسانی روزانه فعال شد.")
    
    # این بخش برای اجرای Flask در یک محیط پروداکشن نیست
    # برای دیباگ و تست محلی مناسب است
    # در محیط پروداکشن از Gunicorn یا uWSGI استفاده کنید
    app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":
    try:
        # چون Flask به تنهایی async نیست، ما asyncio را برای اجرای scheduler مدیریت می‌کنیم
        # و Flask را در نخ اصلی اجرا می‌کنیم.
        # برای سادگی، در اینجا مستقیم app.run را فراخوانی می‌کنیم و scheduler
        # در پس‌زمینه با asyncio کار خواهد کرد.
        
        # نکته: app.run() یک حلقه مسدودکننده است.
        # برای اجرای همزمان scheduler و flask، باید از روش‌های پیشرفته‌تری استفاده کرد.
        # اما برای این پروژه، AsyncIOScheduler با loop پیش‌فرض asyncio کار می‌کند.
        
        # راه حل ساده‌تر:
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()

    except (KeyboardInterrupt, SystemExit):
        logging.info("برنامه متوقف شد.")
