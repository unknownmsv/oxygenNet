# sub_api.py
import json
import base64
import logging
import argparse
from pathlib import Path
from flask import Flask, Response, jsonify

# --- تنظیمات اولیه لاگینگ ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- تابع اصلی تولید محتوای سابسکریپشن ---
def generate_v2ray_subscription(json_file_path: Path) -> str | None:
    """
    Reads a JSON file of V2Ray configs, joins them, and returns a
    base64 encoded subscription string.
    """
    if not json_file_path.exists():
        logging.error(f"فایل کانفیگ V2Ray یافت نشد: {json_file_path}")
        return None

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"خطا در خواندن یا پردازش فایل JSON: {e}")
        return None

    if not isinstance(configs, list) or not configs:
        logging.warning("فایل کانفیگ V2Ray خالی است یا فرمت درستی ندارد.")
        return ""

    config_links = [item['config'] for item in configs if isinstance(item, dict) and 'config' in item]
    full_subscription_text = "\n".join(config_links)
    base64_encoded_sub = base64.b64encode(full_subscription_text.encode('utf-8'))
    return base64_encoded_sub.decode('utf-8')

# --- بخش وب سرور با Flask ---
app = Flask(__name__)

# یک متغیر برای نگهداری مسیر فایل ورودی
# This is a simple way to pass the file path to the Flask endpoint
app.config['INPUT_FILE'] = None

@app.route('/')
def index():
    """صفحه اصلی برای راهنمایی."""
    return jsonify({
        "message": "Subscription server is running.",
        "subscription_link": "/sub"
    })

@app.route('/sub')
def get_subscription():
    """این آدرس، محتوای سابسکریپشن را ارائه می‌دهد."""
    input_file = app.config.get('INPUT_FILE')
    if not input_file:
        return "Error: Input file path not configured.", 500
        
    subscription_content = generate_v2ray_subscription(input_file)
    
    if subscription_content is None:
        return "Error: Could not generate subscription content.", 404
        
    return Response(subscription_content, mimetype='text/plain')

# --- بخش اجرایی اسکریپت ---
def main():
    """تابع اصلی برای اجرای اسکریپت از خط فرمان."""
    parser = argparse.ArgumentParser(
        description="V2Ray Subscription Server.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=Path("configs/v2ray/v2ray_configs.json"),
        help="Path to the input V2Ray configs JSON file."
    )
    
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8787,
        help="Port to run the subscription server on."
    )
    
    parser.add_argument(
        "-H", "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (use 0.0.0.0 for public access)."
    )

    args = parser.parse_args()

    # ذخیره مسیر فایل ورودی برای استفاده در Flask
    app.config['INPUT_FILE'] = args.input

    # نمایش لینک قابل استفاده به کاربر
    print("\n" + "="*50)
    logging.info(f"سرور سابسکریپشن در حال اجرا است...")
    print(f"برای استفاده در کلاینت V2Ray، لینک زیر را کپی کنید:")
    print(f"\n    http://{args.host}:{args.port}/sub\n")
    print(f"نکته: اگر سرور روی کامپیوتر دیگری است، به جای '{args.host}' از IP آن استفاده کنید.")
    print("="*50 + "\n")
    
    # اجرای وب سرور
    app.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
