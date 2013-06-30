# Tools for working with bitmap glyphs
#
# Author: David Coles <coles.david@gmail.com>

import argparse
import logging
import sys
import time

# These are characters recognised as "ink"
INK_CHARS = set(["#", "*", "X"])

def ascii2glyph(ascii_glyph):
    """
    Convert a ASCII glyph to a binary one
    """

    result = []
    for line in ascii_glyph:
        b = 0x00
        for char in line:
            b = b << 1
            if char in INK_CHARS:
                b |= 0x01

        result.append(b)
    return result


# A 5x8 binary glyph
EXAMPLE_GLYPH1 = [
    0b00010,
    0b00011,
    0b00010,
    0b01110,
    0b10010,
    0b10010,
    0b11110,
    0b00000,
]


# A 5x8 binary glyph from ASCII
EXAMPLE_GLYPH2 = ascii2glyph([
    '   # ',
    '   ##',
    '   # ',
    ' ### ',
    '#  # ',
    '#  # ',
    '#### ',
    '     ',
])


if __name__ == "__main__":
    # Test script
    from lis import LISDisplay

    # Debugging
    logging.basicConfig(level=logging.DEBUG)

    # Check that the glyphs are equal
    assert(EXAMPLE_GLYPH1 == EXAMPLE_GLYPH2)

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", required=True)
    args = parser.parse_args()

    with LISDisplay(args.port) as vfd:
        # Write some custom glphs
        vfd.set_char(0x01, EXAMPLE_GLYPH1)
        vfd.set_char(0x02, EXAMPLE_GLYPH2)

        # Print out text
        vfd.write_line(0, "Pnt  1 2 3 4 5 6 7 8")
        vfd.write_line(1, "Glph \x01 \x02 \x03 \x04 \x05 \x06 \x07 \x08")
