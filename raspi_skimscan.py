# file: raspi_skimscan.py
# auth: Tyler Winegarner (twinegarner@gmail.com)
# desc: scans for local bluetooth devices with names matching the description of those
#       used in cas pump credit card skimmers. This software is directly derived from 
#       the research done by Nathan Seidle as documented in this article:
#       https://learn.sparkfun.com/tutorials/gas-pump-skimmers
#

import time
import bluetooth
import sys
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)

font = ImageFont.load_default()
ellipsis = ".   "
phase = 0

time.sleep(3)

while True:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((0, 24), "scanning" + ellipsis, font=font, fill=255)
        disp.image(image)
        disp.display()

	nearby_devices = bluetooth.discover_devices(duration=10, lookup_names=True)

	print("found %d devices" % len(nearby_devices))

	for addr, name in nearby_devices:
		if (name == "HC-05") or (name == "HC-03") or (name == "HC-06"):
			draw.rectangle((0, 0, width, height), outline=0, fill=0)
			draw.text((0, 12), "Potential skimmer", font=font, fill=255)
			draw.text((0, 24), name + " found.", font=font, fill=255)
			draw.text((0, 36), "Skip this pump.", font=font, fill=255)

			disp.image(image)
			disp.display()
			time.sleep(5)

	phase += 1
	if phase == 1:
		ellipsis = "..  "
	elif phase == 2:
		ellipsis = "... "
	elif phase == 3:
		ellipsis = "...."
	else:
		ellipsis = ".   "
		phase = 0

