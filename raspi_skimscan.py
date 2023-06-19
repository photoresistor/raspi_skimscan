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
import json
import logging
import argparse
import threading

from PIL import Image, ImageDraw, ImageFont


def load_config(filename):
    """Load the configuration from a JSON file."""
    with open(filename, 'r') as config_file:
        return json.load(config_file)


def discover_skimmers(config, display):
    """Scan for nearby Bluetooth devices and check for potential skimmers."""
    while True:
        display.draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)
        display.draw.text((0, 24), "Scanning...", font=display.font, fill=255)
        display.display()

        nearby_devices = bluetooth.discover_devices(duration=config['scan_duration'], lookup_names=True)

        logging.info("Found %d devices", len(nearby_devices))

        for addr, name in nearby_devices:
            if name in config['skimmer_names']:
                display.draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)
                display.draw.text((0, 12), "Potential skimmer", font=display.font, fill=255)
                display.draw.text((0, 24), f"{name} found.", font=display.font, fill=255)
                display.draw.text((0, 36), "Skip this pump.", font=display.font, fill=255)

                display.display()
                time.sleep(config['skimmer_alert_duration'])

        time.sleep(config['scan_interval'])


def update_display(display, phase):
    """Update the display with scanning status and ellipsis animation."""
    ellipsis = [".   ", "..  ", "... ", "...."]
    while True:
        display.draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)
        display.draw.text((0, 24), "Scanning" + ellipsis[phase], font=display.font, fill=255)
        display.display()
        time.sleep(1)
        phase = (phase + 1) % 4


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Scan for potential credit card skimmers.')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Initialize logging
    logging.basicConfig(filename=config['log_file'], level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    try:
        # Initialize OLED display
        display = Adafruit_SSD1306.SSD1306_128_64(rst=config['pin_config']['RST'],
                                                  dc=config['pin_config']['DC'],
                                                  spi=SPI.SpiDev(config['spi_config']['SPI_PORT'],
                                                                 config['spi_config']['SPI_DEVICE'],
                                                                 max_speed_hz=config['spi_config']['SPI_SPEED']))

        display.begin()
        time.sleep(3)
        display.clear()
        display.display()

        # Create image and font objects
        image = Image.new('1', (display.width, display.height))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        # Set up display and scanning threads
        scanning_thread = threading.Thread(target=discover_skimmers, args=(config, display))
        display_thread = threading.Thread(target=update_display, args=(display, 0))

        # Start both threads
        scanning_thread.start()
        display_thread.start()

        # Wait for threads to complete
        scanning_thread.join()
        display_thread.join()

    except Exception as e:
        logging.exception("An error occurred: %s", str(e))


if __name__ == '__main__':
    main()
