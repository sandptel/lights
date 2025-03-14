import json
import logging
import asyncio
import sys
from tuya_integration import login_to_tuya, get_devices, change_color
from file_monitor import monitor_file_and_update_devices
from tuyapy import TuyaApi
from connection_state import save_state

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("daemon.log")
    ]
)

logger = logging.getLogger()


async def main():
    try:
        api = TuyaApi()

        with open('config.json') as config:
            data = json.load(config)

        username = data['username']
        password = data['password']
        country_code = data['country_code']
        application = data['application']

        while True:
            logger.info(f"Logging in for {username}")
            devices, error = login_to_tuya(api, username, password, country_code, application)

            if error:
                logger.error(f"Initialization failed: {error}")
                save_state("waiting")
                await asyncio.sleep(180)  # Wait for 180 seconds if login failed due to rate limit
                continue

            logger.info(f"Discovered devices: {list(get_devices(api).keys())}")
            await monitor_file_and_update_devices('colors.json', devices, change_color)

    except Exception as e:
        logger.error(f"Critical error occurred: {e}")
        save_state("broken")
        sys.exit(1)
