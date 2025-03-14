import json
import asyncio
from watchfiles import awatch
from color_utils import hex_to_rgb, rgb_to_hsv

async def change_color(devices, r, g, b):
    h, s, v = rgb_to_hsv(r, g, b)
    if v < 5 or s < 10:
        h, s, v = 210, 4, 19  # Adjust for near black/white/gray colors
    await asyncio.gather(*(asyncio.to_thread(device.set_color, (h, s, v)) for device in devices))

async def monitor_file_and_update_devices(file_path, devices):
    old_color = None
    async for changes in awatch(file_path):
        try:
            with open(file_path, 'r') as file:
                colors = json.load(file)
                hex_code = colors.get("colors", {}).get("color10")
                if not hex_code:
                    print("No color10 found in colors.json")
                    continue

                new_color = hex_to_rgb(hex_code)
                if new_color != old_color:
                    await change_color(devices, *new_color)
                    print(f"Changed color to {new_color}")
                    old_color = new_color

        except Exception as e:
            print(f"Error processing file change: {repr(e)}")
