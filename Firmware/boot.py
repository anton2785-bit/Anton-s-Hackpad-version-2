# boot.py - XIAO RP2040
# Enables the secondary USB serial port used for receiving PC stats

import usb_cdc
usb_cdc.enable(data=True)
