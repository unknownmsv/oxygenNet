# main.py
import asyncio
import logging
import subprocess
import sys
import atexit
from configs import miner

# --- Initial Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variable to hold the subscription server process
sub_api_process = None

def start_subscription_server():
    """Runs sub_api.py as a separate process."""
    global sub_api_process
    logger.info("Starting subscription server...")
    try:
        # Run sub_api.py using the same Python interpreter that executed main.py
        sub_api_process = subprocess.Popen([sys.executable, 'sub_api.py'])
        logger.info(f"✅ Subscription server started successfully with PID: {sub_api_process.pid}")
    except FileNotFoundError:
        logger.error("Error: sub_api.py file not found. Please ensure the file exists in the correct path.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running sub_api.py: {e}")
        sys.exit(1)

def cleanup():
    """Cleanup function that runs when exiting the program."""
    logger.info("Stopping background processes...")
    if sub_api_process:
        sub_api_process.terminate()
        sub_api_process.wait()
        logger.info("Subscription server stopped.")

async def hourly_update_task():
    """Main task that runs hourly."""
    logger.info("--- Starting hourly config update task ---")
    try:
        await miner.main()
    except Exception as e:
        logger.error(f"Error in miner execution: {e}")
    logger.info("--- Hourly update task completed ---")

async def main():
    # Register cleanup function to run on exit
    atexit.register(cleanup)

    # 1. Start subscription server in background
    start_subscription_server()
    
    # 2. Main loop for hourly task execution
    try:
        while True:
            # Execute update task
            await hourly_update_task()
            
            # Wait for one hour
            update_interval_seconds = 3600
            logger.info(f"Next execution in {int(update_interval_seconds / 60)} minutes...")
            await asyncio.sleep(update_interval_seconds)

    except (KeyboardInterrupt, SystemExit):
        logger.info("Exit request received. Shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"An unexpected error occurred in main program: {e}")
    finally:
        logger.info("OxygenNet program terminated.")