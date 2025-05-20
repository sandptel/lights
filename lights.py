import asyncio
import json
import sys
from connection_manager import ConnectionManager
from file_monitor import monitor_file_and_update_devices

async def main():
    try:
        # Load configuration
        with open('config.json') as config_file:
            config = json.load(config_file)
        
        manager = ConnectionManager(config)
        
        # Initialize connection
        devices = await manager.initialize_connection()
        if not devices:
            sys.exit(1)  # Exit if initialization fails
        
        # Monitor colors.json for updates
        await monitor_file_and_update_devices('colors.json', devices)
    
    except KeyboardInterrupt:
        print("Exiting...")
        await manager.update_state("disconnected")
        sys.exit(0)

if __name__ == '__main__':
    asyncio.run(main())
