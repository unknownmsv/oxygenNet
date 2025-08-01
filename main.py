# main.py
import asyncio
import logging
import subprocess
import sys
import atexit

# وارد کردن ماژول ماینر
from configs import miner

# --- تنظیمات اولیه ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# متغیری برای نگهداری فرآیند سرور سابسکریپشن
sub_api_process = None

def start_subscription_server():
    """فایل sub_api.py را به عنوان یک فرآیند جداگانه اجرا می‌کند."""
    global sub_api_process
    logger.info("در حال راه‌اندازی سرور سابسکریپشن...")
    try:
        # اجرای sub_api.py با استفاده از همان مفسر پایتونی که main.py را اجرا کرده
        sub_api_process = subprocess.Popen([sys.executable, 'sub_api.py'])
        logger.info(f"✅ سرور سابسکریپشن با موفقیت با PID: {sub_api_process.pid} اجرا شد.")
    except FileNotFoundError:
        logger.error("خطا: فایل sub_api.py یافت نشد. لطفاً از وجود فایل در مسیر درست اطمینان حاصل کنید.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"خطا در اجرای sub_api.py: {e}")
        sys.exit(1)

def cleanup():
    """تابع پاکسازی که هنگام خروج از برنامه اجرا می‌شود."""
    logger.info("در حال متوقف کردن فرآیندهای پس‌زمینه...")
    if sub_api_process:
        sub_api_process.terminate()
        sub_api_process.wait()
        logger.info("سرور سابسکریپشن متوقف شد.")

async def hourly_update_task():
    """وظیفه اصلی که به صورت ساعتی اجرا می‌شود."""
    logger.info("--- شروع وظیفه به‌روزرسانی ساعتی کانفیگ‌ها ---")
    try:
        await miner.main()
    except Exception as e:
        logger.error(f"خطا در اجرای ماینر: {e}")
    logger.info("--- وظیفه به‌روزرسانی ساعتی به پایان رسید ---")

async def main():
    # ثبت تابع cleanup برای اجرا شدن هنگام خروج
    atexit.register(cleanup)

    # ۱. راه‌اندازی سرور سابسکریپشن در پس‌زمینه
    start_subscription_server()
    
    # ۲. حلقه اصلی برای اجرای ساعتی وظیفه
    try:
        while True:
            # اجرای وظیفه به‌روزرسانی
            await hourly_update_task()
            
            # انتظار برای یک ساعت
            update_interval_seconds = 3600
            logger.info(f"اجرای بعدی تا {int(update_interval_seconds / 60)} دقیقه دیگر...")
            await asyncio.sleep(update_interval_seconds)

    except (KeyboardInterrupt, SystemExit):
        logger.info("درخواست خروج دریافت شد. برنامه در حال خاموش شدن است.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"یک خطای پیش‌بینی نشده در برنامه اصلی رخ داد: {e}")
    finally:
        logger.info("برنامه OxygenNet به پایان رسید.")
