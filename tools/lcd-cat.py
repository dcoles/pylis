#!/usr/bin/env python
# Script for printing to LCD display
#
# Author: David Coles <coles.david@gmail.com>

import argparse
import time
import logging
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
from pylis.lis import LISDisplay, NCHARS, LINES

DEFAULT_DELAY = 0.5 # sec

def show_lines(vfd, lines, delay=DEFAULT_DELAY):
    """
    Display multiple lines on a display by scrolling through them.
    If the line is wider than the display, it will be truncated.
    """
    display = [""]*LINES
    while True:
        line = lines.readline()
        if line == "":
            break
        display.append(line.rstrip())
        display.pop(0)
        for i, d in enumerate(display):
            vfd.write_line(i, d.ljust(NCHARS))
        time.sleep(delay)


if __name__ == "__main__":
    # Uncomment for debugging
    #logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", required=True)
    parser.add_argument("-d", "--delay", type=float, default=DEFAULT_DELAY)
    args = parser.parse_args()

    with LISDisplay(args.port) as vfd:
        show_lines(vfd, sys.stdin, delay=args.delay)
