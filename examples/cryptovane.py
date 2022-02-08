#!/usr/bin/python
# -*- coding:utf-8 -*-

# Python E-Ink 2.13in Two Color Crypto Fear and Greed Display
# 1. Make api call and create variables of data
# 2. Use pillow to draw data to appropriate image
# 3. Each image is a combination black layer and red layer drawn to two bmp files
# 4. Initialize and draw bmp to e-paper hat
# 5. Sleep and low power until next update

# Initialize and import libraries
from PIL import Image, ImageDraw, ImageFont
import psutil
import traceback
import time
import logging
import urllib.request
import json
import sys
import os
# Import location of e-paper libs and images
picdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
    
# Init library for epd paper hat
from waveshare_epd import epd2in13b_V3
# Init model of e-paper hat
epd = epd2in13b_V3.EPD()

# Init fonts
font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
font44 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 44)

# Sleep in case first boot
print('Sleeping 20 seconds before first startup...')
time.sleep(20)

# 1. --------------- Get Fear and Greed Data from API ---------------

# Convert seconds to readable format


def convert(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


# Test dictionary
test_dict = {'name': 'Fear and Greed Index', 'data': [{'value': '20', 'value_classification': 'Extreme Fear', 'timestamp': '1643846400', 'time_until_update': '70732'}, {
    'value': '28', 'value_classification': 'Fear', 'timestamp': '1643760000'}], 'metadata': {'error': None}}


# Get current time, create data from api call to dictionary
unixtime = int(time.time())
fgindex = urllib.request.urlopen('https://api.alternative.me/fng/?limit=2')
raw_data = json.loads(fgindex.read().decode("utf-8"))
data = raw_data['data']

# Grab values from data
x = (item["value"] for item in data)
current_fgi_number = next(x)
previous_fgi_number = next(x)

mood = (item["value_classification"] for item in data)
mood = next(mood)

update_time = (item['time_until_update'] for item in data)
ut = next(update_time)
ut = int(ut)
next_update = 60 + ut
display_next_update = convert(ut)

# Print api results to console
print('Current Value: ' + current_fgi_number)
print('Mood: ' + mood)
print('Previous Value: ' + previous_fgi_number)
print('Current Unix Time: ' + time.strftime("%I:%M %p", time.gmtime(unixtime)))
print('Current Local Time: ' + time.strftime("%I:%M %p", time.localtime(unixtime)))
print('Next Update Timer: ' + display_next_update)
print('Seconds to Next Update: ' + str(next_update))

# 2. --------------- Draw Images from API Data ---------------

# Create black layer, red layer, save layers to b_current.bmp and r_current.bmp
# Get current mood and set black base layer
try:
    if mood == 'Extreme Fear':
        base_layer = 'extremefear.bmp'
    elif mood == 'Fear':
        base_layer = 'fear.bmp'
    elif mood == 'Neutral':
        base_layer = 'neutral.bmp'
    elif mood == 'Greed':
        base_layer = 'greed.bmp'
    elif mood == 'Extreme Greed':
        base_layer = 'extremegreed.bmp'
    else:
        logging.info("Can't create base layer!")
except IOError as e:
    logging.info(e)

# 3. --------------- Draw Red and Black Layers --------------

# Determine red layer if any and create red layer as r_current.bmp else use null.bmp
try:
    if mood in ['Fear', 'Extreme Fear']:
        r_current = Image.open(os.path.join(picdir, 'null.bmp'))
        draw = ImageDraw.Draw(r_current)
        draw.text((125, 25), current_fgi_number, (1, 1, 1), font=font44)
    else:
        r_current = Image.open(os.path.join(picdir, 'null.bmp'))
    r_current.save('r_current.bmp')
except IOError as e:
    logging.info(e)

# Draw black layer and save to b_current.bmp and if not in Fear or EFear, draw current fgi number as well
b_current = Image.open(os.path.join(picdir, 'null.bmp'))
try:
    if mood == 'Extreme Fear':
        blackcurrent = Image.open(os.path.join(picdir, 'extremefear.bmp'))
    elif mood == 'Fear':
        blackcurrent = Image.open(os.path.join(picdir, 'fear.bmp'))
    elif mood == 'Greed':
        blackcurrent = Image.open(os.path.join(picdir, 'greed.bmp'))
    elif mood == 'Neutral':
        blackcurrent = Image.open(os.path.join(picdir, 'neutral.bmp'))
    elif mood == 'Extreme Greed':
        blackcurrent = Image.open(os.path.join(picdir, 'extremegreed.bmp'))
except IOError as e:
    logging.info(e)

draw = ImageDraw.Draw(b_current)
b_current.paste(blackcurrent, (0, 0))
draw.text((105, 5), "Previous: " + previous_fgi_number,
          (1, 1, 1), font=font16)

try:
    draw.text((125, 25), current_fgi_number, (1, 1, 1), font=font44)
except IOError as e:
    logging.info(e)

b_current.save('b_current.bmp')

# 4. --------------- Init and draw bmp files to e-paper hat ---------------
try:
    epd.init()
    epd.Clear()
    time.sleep(1)
    logging.info("Draw to e-paper hat")
# Rotate image 180 degrees so micro usb is on top
    b_current = b_current.transpose(Image.ROTATE_180)
    r_current = r_current.transpose(Image.ROTATE_180)
    epd.display(epd.getbuffer(b_current), epd.getbuffer(r_current))
    epd.sleep()
except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c")
    epd2in13b_V3.epdconfig.module_exit()
    exit()

# 5. --------------- Update interval script ---------------


def restart_program():
    # Restarts the current program, with file objects and descriptors cleanup
    try:
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)
    except KeyboardInterrupt:
        logging.info("ctrl + c")
        exit()

    python = sys.executable
    os.execl(python, python, *sys.argv)


logging.info("Sleeping until next update...")
time.sleep(next_update)
restart_program()
