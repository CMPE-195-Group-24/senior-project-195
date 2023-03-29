import RPi.GPIO as GPIO
import pn532.pn532 as nfc
import sys
sys.path.append('../')
from gpiozero import RGBLED
from pn532 import *
from DFRobot_RGBLCD1602 import *
import time

pn532 = PN532_I2C(debug=False, reset=20, req=16)

ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure the GPIO pins of the RGB LED
# Red = pin 21, Green = pin 20, Blue = pin 16
led = RGBLED(21, 20, 16)

# Configure 16x2 LCD text screen
lcd=DFRobot_RGBLCD1602(rgb_addr=0x60,col= 16,row = 2)

# Configures the PN532 to communicate with MiFare cards
pn532.SAM_configuration()

# This section waits for the Apple Digital card and scans the UID into the comptuter
# print('Waiting for RFID/NFC card...')
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)

            # To turn LED on, select R, G, B to be 1 for color
            led.color(1, 0, 0)

            print('.', end = "")
            # Try again if no card is available.
            if uid is None:
                continue
            
            # This prints into the console of the computer
            # print('Found card with UID:', [hex(i) for i in uid])

    except Exception as e:
        print(e)