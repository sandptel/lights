import asyncio
import json
from datetime import datetime
from tuyapy import TuyaApi

class ConnectionManager:
    def __init__(self, config):
        self.api = TuyaApi()
        self.username = config['username']
        self.password = config['password']
        self.country_code = config['country_code']
        self.application = config['application']
        self.retry_count = 0
        self.max_retries = 3
        self.state_file = 'connection.json'

    async def initialize_connection(self):
        try:
            self.api.init(self.username, self.password, self.country_code, self.application)
            await self.update_state("connected")
            devices = self.api.get_all_devices()
            return [device for device in devices if device.obj_type == 'light']
        except Exception as e:
            print(f"Connection failed: {repr(e)}")
            await self.update_state("waiting")
            return await self.retry_connection()

    async def retry_connection(self):
        while self.retry_count < self.max_retries:
            self.retry_count += 1
            wait_time = 2 ** self.retry_count 
            print(f"Retrying connection in {wait_time} seconds... (Attempt {self.retry_count})")
            await asyncio.sleep(wait_time)
            try:
                self.api.init(self.username, self.password, self.country_code, self.application)
                await self.update_state("connected")
                devices = self.api.get_all_devices()
                return [device for device in devices if device.obj_type == 'light']
            except Exception as e:
                print(f"Retry {self.retry_count} failed: {repr(e)}")
        await self.update_state("broken")
        print("Max retries exceeded. Entering broken state.")
        return None

    async def update_state(self, state):
        state_data = {
            "text": "1","alt": state,"tooltip": "Connection state","class": state}

            # "text": state,
            # "last_updated": datetime.now().isoformat(),
            # "retry_count": self.retry_count,
        
        with open(self.state_file, 'w') as file:
            json.dump(state_data, file, indent=4)
