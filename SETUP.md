# Setup Guide

## Deploying to Raspberry Pi Zero 2 W

The code must run on the Raspberry Pi since it accesses GPIO and SPI hardware directly.

### Option 1: Copy files with scp

```bash
scp -r demo_code/Raspberry-Pi_2.13_V2/python pi@<pi-ip>:~/epaper
```

### Option 2: Sync with rsync (useful for ongoing development)

```bash
rsync -av demo_code/Raspberry-Pi_2.13_V2/python/ pi@<pi-ip>:~/epaper/
```

### Option 3: Clone repo directly on Pi

```bash
ssh pi@<pi-ip>
git clone <your-repo-url> ~/epaper-project
```

## Installing Dependencies on the Pi

```bash
sudo apt update
sudo apt install python3-pip python3-spidev python3-gpiozero python3-numpy python3-pil
```

## Enable SPI

SPI must be enabled on the Raspberry Pi:

```bash
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable
# Reboot if prompted
```

## Testing the Display

Save the following as `test_display.py` in the same directory as `epd_2inch13.py`:

```python
#!/usr/bin/env python3
"""Simple e-Paper display test - clears screen to white then black."""

from epd_2inch13 import EPD_2Inch13
import time

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
```

Run the test:

```bash
cd ~/epaper
python3 test_display.py
```

### Expected Behavior

If working correctly, you should see:
1. Screen clears to white
2. Screen fills black
3. Screen clears to white again

The flicker during refresh is normal for e-paper displays.

## Troubleshooting

### Permission denied on SPI

Run with sudo or add your user to the spi group:

```bash
sudo usermod -aG spi $USER
# Log out and back in for changes to take effect
```

### Display not responding

1. Verify wiring matches the pinout in README.md
2. Check that SPI is enabled: `ls /dev/spi*` should show `/dev/spidev0.0`
3. Ensure the display is receiving 3.3V power
