#!/usr/bin/env python3
"""Simple e-Paper display test - clears screen to white then black."""

import time

from epd_2inch13 import EPD_2Inch13

epd = EPD_2Inch13()

try:
    print("Initializing display...")
    epd.hw_init()

    print("Clearing to white...")
    epd.whitescreen_white()
    time.sleep(2)

    print("Filling black...")
    epd.write_cmd(0x24)
    for _ in range(4000):
        epd.write_data(0x00)
    epd.update()
    time.sleep(2)

    print("Clearing to white...")
    epd.whitescreen_white()

    print("Done! Entering sleep mode.")
    epd.sleep()

except KeyboardInterrupt:
    print("Interrupted")
    epd.sleep()
finally:
    epd.clean_gpio()
