# sub_api.py
import json
import base64
import logging
import time
from pathlib import Path
from flask import Flask, Response
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Initial Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Global Variables ---
CONFIG_FILE = Path("configs/v2ray/v2ray_configs.json")
# Subscription content is cached here for faster response
CACHED_SUB_CONTENT = ""

def update_subscription_cache():
    """
    Reads the JSON file, generates subscription content and caches it in memory.
    """
    global CACHED_SUB_CONTENT
    logger.info("Attempting to update subscription cache...")
    
    if not CONFIG_FILE.exists():
        logger.warning(f"Config file not found: {CONFIG_FILE}")
        CACHED_SUB_CONTENT = ""
        return

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        
        config_links = [item['config'] for item in configs if isinstance(item, dict) and 'config' in item]
        full_subscription_text = "\n".join(config_links)
        base64_encoded_sub = base64.b64encode(full_subscription_text.encode('utf-8'))
        CACHED_SUB_CONTENT = base64_encoded_sub.decode('utf-8')
        logger.info(f"✅ Subscription cache successfully updated with {len(config_links)} configs.")

    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading/processing JSON file: {e}")
        CACHED_SUB_CONTENT = ""

class ConfigChangeHandler(FileSystemEventHandler):
    """
    Class that reacts to changes in the config file.
    """
    def on_modified(self, event):
        if not event.is_directory and Path(event.src_path) == CONFIG_FILE:
            logger.info("Config file change detected!")
            update_subscription_cache()

# --- Flask Web Server Setup ---
app = Flask(__name__)

@app.route('/sub')
def get_subscription():
    """This endpoint serves the cached subscription content."""
    return Response(CACHED_SUB_CONTENT, mimetype='text/plain')

def main():
    # Initialize cache on startup
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    update_subscription_cache()

    # Setup Watchdog to monitor the file
    event_handler = ConfigChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=CONFIG_FILE.parent, recursive=False)
    observer.start()
    logger.info(f"Subscription server started and monitoring {CONFIG_FILE}")

    try:
        # Run web server
        app.run(host='0.0.0.0', port=8787)
    finally:
        observer.stop()
        observer.join()
        logger.info("Subscription server stopped.")

if __name__ == "__main__":
    main()