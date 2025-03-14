import json
import sys
import os
import traceback
import pyscreenshot as image_grab
from tuyapy import TuyaApi

from colorthief import ColorThief

api = TuyaApi()


def turn_off(device):
    if not isinstance(device, list):
        return device.turn_off()
    else:
        return [i.turn_off() for i in device]


def turn_on(device):
    if not isinstance(device, list):
        return device.turn_on()
    else:
        return [i.turn_on() for i in device]


def change_color(device, r, g, b):
    # Manually adjusting for black white and gray
    h, s, v = rgb_to_hsv(r, g, b)
    if v < 5 or s < 10:
        print("Adjusting from {} to {}".format(str(v),str((210, 4 , 19))))
        h = 210
        s = 4
        v = 19
    change_color_from_hsv(device, h, s, v)


def change_color_from_rgb(device, r, g, b):
    if not isinstance(device, list):
        return device.set_color(rgb_to_hsv(r, g, b))
    else:
        return [i.set_color(rgb_to_hsv(r, g, b)) for i in device]


def change_color_from_hsv(device, h, s, v):
    if not isinstance(device, list):
        return device.set_color((h, s, v))
    else:
        return [i.set_color((h, s, v)) for i in device]


def rgb_to_hsv(r, g, b):
    # Reference: https://www.w3resource.com/python-exercises/math/python-math-exercise-77.php
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    h = 0
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    elif mx == b:
        h = (60 * ((r - g) / df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df / mx) * 100
    v = mx * 100
    return h, s, v

def hex_to_rgb(hex_code):
    """
    Convert a hexadecimal color code to an RGB tuple.

    Args:
        hex_code (str): A string representing the hex color code, e.g., "#FFFFFF" or "FFFFFF".

    Returns:
        tuple: A tuple of integers (red, green, blue), each in the range 0-255.
    """
    # Remove the '#' character if present
    hex_code = hex_code.lstrip('#')
    
    # Ensure the hex code is valid (length of 6 characters)
    if len(hex_code) != 6:
        raise ValueError("Invalid hex code. A valid hex code must have exactly 6 characters.")
    
    # Convert the hex code to an RGB tuple
    red = int(hex_code[0:2], 16)
    green = int(hex_code[2:4], 16)
    blue = int(hex_code[4:6], 16)
    
    return red, green, blue


# Example usage
# Uncomment the following lines to test the function
# hex_code = "#34A2FE"
# rgb = hex_to_rgb(hex_code)
# print(f"Hex: {hex_code} -> RGB: {rgb}")



if __name__ == '__main__':
    with open('config.json') as config:
        data = json.load(config)
    username = data['username']
    password = data['password']
    country_code = data['country_code']
    application = data['application']
    print("Logging in for {}".format(username))
    api.init(username, password, country_code, application)
    device_ids = api.get_all_devices()
    lights = dict(sorted(dict((i.name(), i) for i in device_ids if i.obj_type == 'light').items()))
    devices = {**lights}
    print(devices)
    devices_list = [*devices.values()]
    # colors = json.load("colors.json")
    # hex_code = "#34A2FE"
    old_color = (0, 0, 0)
    # change_color(devices_list, dominant_color[0], dominant_color[1], dominant_color[2])
    while True:
        try:
            # TODO get screensize and set dynamic margin
            # fss = image_grab.grab(bbox=(204, 115, 1162, 653))
            # color_thief = ColorThief(fss, is_obj=True)
            # get the dominant color
            # dominant_color = color_thief.get_color(quality=5, ignore_white=True, ignore_black=True)
            with open('colors.json') as colors:
                    colors = json.load(colors)
                    hex_code = colors["colors"]["color2"]
                    print(hex_code)
                    dominant_color = hex_to_rgb(hex_code)
                    print(dominant_color)
            if old_color == dominant_color:
                continue
            else:
                change_color(devices_list, dominant_color[0], dominant_color[1], dominant_color[2])
                print("Changed colour to " + str(dominant_color))
                old_color = dominant_color
        except KeyboardInterrupt:
            print('OK bye!')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except Exception as e:
            print("Failed to due to " + repr(e))
            print(traceback.format_exc())




