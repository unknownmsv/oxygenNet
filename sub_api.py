# sub_api.py
import json
import base64
import logging
import time
from pathlib import Path
from flask import Flask, Response
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- تنظیمات اولیه ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- متغیرهای گلوبال ---
CONFIG_FILE = Path("configs/v2ray/v2ray_configs.json")
# محتوای سابسکریپشن در این متغیر کش می‌شود تا سرعت پاسخ‌دهی بالا برود
CACHED_SUB_CONTENT = ""

def update_subscription_cache():
    """
    فایل JSON را می‌خواند، محتوای سابسکریپشن را تولید و در حافظه کش می‌کند.
    """
    global CACHED_SUB_CONTENT
    logger.info("تلاش برای به‌روزرسانی کش سابسکریپشن...")
    
    if not CONFIG_FILE.exists():
        logger.warning(f"فایل کانفیگ یافت نشد: {CONFIG_FILE}")
        CACHED_SUB_CONTENT = ""
        return

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        
        config_links = [item['config'] for item in configs if isinstance(item, dict) and 'config' in item]
        full_subscription_text = "\n".join(config_links)
        base64_encoded_sub = base64.b64encode(full_subscription_text.encode('utf-8'))
        CACHED_SUB_CONTENT = base64_encoded_sub.decode('utf-8')
        logger.info(f"✅ کش سابسکریپشن با موفقیت با {len(config_links)} کانفیگ به‌روز شد.")

    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"خطا در خواندن یا پردازش فایل JSON: {e}")
        CACHED_SUB_CONTENT = ""

class ConfigChangeHandler(FileSystemEventHandler):
    """
    کلاسی که به تغییرات در فایل کانفیگ واکنش نشان می‌دهد.
    """
    def on_modified(self, event):
        if not event.is_directory and Path(event.src_path) == CONFIG_FILE:
            logger.info("تغییر در فایل کانفیگ شناسایی شد!")
            update_subscription_cache()

# --- راه‌اندازی وب سرور Flask ---
app = Flask(__name__)

@app.route('/sub')
def get_subscription():
    """این آدرس، محتوای کش شده سابسکریپشن را ارائه می‌دهد."""
    return Response(CACHED_SUB_CONTENT, mimetype='text/plain')

def main():
    # در ابتدای اجرا، یک بار کش را مقداردهی می‌کند
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    update_subscription_cache()

    # راه‌اندازی Watchdog برای زیر نظر گرفتن فایل
    event_handler = ConfigChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=CONFIG_FILE.parent, recursive=False)
    observer.start()
    logger.info(f"سرور سابسکریپشن شروع به کار کرد و فایل {CONFIG_FILE} را زیر نظر دارد.")

    try:
        # اجرای وب سرور
        app.run(host='0.0.0.0', port=8787)
    finally:
        observer.stop()
        observer.join()
        logger.info("سرور سابسکریپشن متوقف شد.")

if __name__ == "__main__":
    main()
