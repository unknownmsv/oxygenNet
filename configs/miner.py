# miner.py
import os
import asyncio
import json
import re
import logging
from pathlib import Path
from telethon import TelegramClient
from dotenv import load_dotenv

# --- Initial Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = 'telegram_session'

if not API_ID or not API_HASH:
    raise ValueError("Please set API_ID and API_HASH in the .env file.")

# --- Channels and Paths ---
V2RAY_CHANNELS = ['@v2rayconfig', '@PrivateVPNs', '@FreeV2rays']
WIREGUARD_CHANNELS = ['@ConfigWireguard', '@WireGuardConfigs']

OUTPUT_DIR = Path("configs")
# NEW: Path for the JSON output file
V2RAY_JSON_FILE = OUTPUT_DIR / "v2ray" / "v2ray_configs.json"
WIREGUARD_OUTPUT_DIR = OUTPUT_DIR / "wireguard"

# --- Regular Expressions ---
V2RAY_REGEX = r'(?:vmess|vless|trojan)://[^\s`"<]+'
WIREGUARD_BLOCK_REGEX = r'(\[Interface\][\s\S]*?\[Peer\][\s\S]*?Endpoint\s*=\s*.*)'
WIREGUARD_LINK_REGEX = r'wireguard://[^\s`"<]+'


async def process_v2ray_configs(client: TelegramClient):
    """Extracts V2Ray configs and stores them in a structured JSON file."""
    logging.info("Starting V2Ray config extraction...")
    unique_configs = set()

    for channel in V2RAY_CHANNELS:
        try:
            logging.info(f"Checking channel: {channel}")
            async for message in client.iter_messages(channel, limit=200):
                if message.text:
                    found = re.findall(V2RAY_REGEX, message.text)
                    for config in found:
                        unique_configs.add(config)
        except Exception as e:
            logging.error(f"Error accessing channel {channel}: {e}")

    if not unique_configs:
        logging.warning("No V2Ray configs found.")
        return

    # NEW: Create a list of dictionaries with IDs
    configs_with_id = [
        {"id": i + 1, "config": config_str}
        for i, config_str in enumerate(unique_configs)
    ]

    # Ensure destination directory exists
    V2RAY_JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # NEW: Save as a JSON file
    with open(V2RAY_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(configs_with_id, f, indent=2, ensure_ascii=False)

    logging.info(f"✅ V2Ray: {len(configs_with_id)} configs saved to:\n{V2RAY_JSON_FILE}")

async def process_wireguard_configs(client: TelegramClient):
    """Extracts WireGuard configs and saves each in a separate .conf file."""
    logging.info("Starting WireGuard config extraction...")
    
    unique_configs = set()

    for channel in WIREGUARD_CHANNELS:
        try:
            logging.info(f"Checking channel: {channel}")
            async for message in client.iter_messages(channel, limit=200):
                if not message.text:
                    continue
                
                text_blocks = re.findall(WIREGUARD_BLOCK_REGEX, message.text)
                for block in text_blocks:
                    unique_configs.add(block.strip())
                
                links = re.findall(WIREGUARD_LINK_REGEX, message.text)
                for link in links:
                    try:
                        config_str = " ".join(link.replace("wireguard://", "").split(","))
                        unique_configs.add(config_str)
                    except Exception as e:
                        logging.warning(f"Error processing WireGuard link: {e}")

        except Exception as e:
            logging.error(f"Error accessing channel {channel}: {e}")

    if not unique_configs:
        logging.warning("No WireGuard configs found.")
        return

    WIREGUARD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for i, config in enumerate(unique_configs):
        file_path = WIREGUARD_OUTPUT_DIR / f"wg_{i+1}.conf"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(config)

    logging.info(f"✅ WireGuard: {len(unique_configs)} configs saved to:\n{WIREGUARD_OUTPUT_DIR}")

async def main():
    """Main function to connect to Telegram and run processes."""
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        logging.info("Telegram client connected successfully.")
        await process_v2ray_configs(client)
        await process_wireguard_configs(client)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, TypeError) as e:
        logging.error(f"Input error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        logging.info("Script finished.")