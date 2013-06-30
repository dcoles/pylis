# Module for interfacing with VLSystem's L.I.S. MCE display
#
# Author: David Coles <coles.david@gmail.com>

# This display is a 20x2 HD44780 Display connected to a FTDI USB Serial
# controller.

import argparse
import time
import logging
import sys

import serial


LOGGER = logging.getLogger(__name__)

# TTY settings
DEFAULT_BAUD = 38400

# Command strings for LIS USB module
# Note: Since there's no official documentation for this module, most of it has
# been reverse-engineered from watching traffic from the official Windows app.

# Used in some commands
CMD_NULL = 0x00
# Reset display: [CMD_RESET] (need to wait a bit...)
CMD_RESET = 0xA0
# Set display line: [CMD_LINES[i]]
CMD_LINES = [0xA1, 0xA2]
# ???
CMD_A3 = 0xA3
# ???
CMD_A4 = 0xA4
# ???
CMD_A5 = 0xA5
# Write string: [CMD_WRITE] + str + [CMD_NULL]
CMD_WRITE = 0xA7
# ???
CMD_AA = 0xAA
# Set character line: [CMD_SETCHAR, chr, line, data]
CMD_SETCHAR = 0xAB

# Glyph specifications
CHAR_WIDTH = 5
CHAR_HEIGHT = 8
CHAR_MASK = 2**CHAR_WIDTH - 1

# Display specifications
NCHARS = 20
LINES = 2


class LISDisplay(object):
    """
    Interface to control the L.I.S Display.
    """
    tty = None

    def __init__(self, port):
        """
        Create a new LISDisplay.

        :param port: The serial port the display is connected to.
        """
        self.tty = serial.Serial(port, baudrate=DEFAULT_BAUD, bytesize=8, stopbits=1, parity='N')
        self.reset()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def _writebytes(self, b):
        """
        Write bytes directly to the device.
        """
        b = serial.to_bytes(b)
        LOGGER.debug("Write: %r", b)
        self.tty.write(b)
        self.tty.flush()

        # XXX: Writing commands too fast seems to cause errors
        time.sleep(0.01)

    def reset(self):
        """
        Reset the device, clearing the screen in the process.
        Custom glyphs are maintained.
        """
        self._writebytes([CMD_RESET])

        # XXX: Need to wait a bit after a reset
        time.sleep(0.1)

    def set_char(self, c, glyph):
        """
        Set a custom glyph.
        A glyph is a list of bytes where each byte is the bitmask for that line of the glyph.
        """
        if len(glyph) != CHAR_HEIGHT:
            raise ValueError("Invalid number of lines in glyph (expected {0})".format(CHAR_HEIGHT))

        LOGGER.info("Set char: 0x%X", c)

        for i, row in enumerate(glyph):
            LOGGER.debug("l %d", i)
            self._writebytes([CMD_SETCHAR, c, i, (row & CHAR_MASK)])
        self._writebytes([CMD_NULL])

    def line(self, n):
        """
        Set the line to write to. This will also move the cursor back to the start.
        The first line has index 0.
        """
        LOGGER.info("Line: %d", n)
        self._writebytes([CMD_LINES[n], CMD_NULL])

    def write_bytes(self, b):
        """
        Write raw bytes at the current cursor position.
        """
        b = serial.to_bytes(b)
        LOGGER.info("Byte string: %r", b)
        self._writebytes([CMD_WRITE])
        self._writebytes(b)
        self._writebytes([CMD_NULL])

    def write_line(self, n, s):
        """
        Write a new string to line `n`.
        """
        self.line(n)
        self.write_bytes(s.encode('ascii'))

    def close(self):
        """
        Close this device.
        """
        self.tty.close()
        self.tty = None


if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", required=True)
    args = parser.parse_args()

    with LISDisplay(args.port) as vfd:
        vfd.write_line(0, "Hello, World! ^_^")
        vfd.line(1)
        vfd.write_bytes([0xff-i for i in range(20)])
