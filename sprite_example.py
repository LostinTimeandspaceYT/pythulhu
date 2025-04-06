# SPDX-FileCopyrightText: 2019 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
import displayio
import adafruit_imageload
from hardware import HAL


# Load the sprite sheet (bitmap)
sprite_sheet, palette = adafruit_imageload.load("/example.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

# Create a sprite (tilegrid)
sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                            width = 1,
                            height = 1,
                            tile_width = 43,
                            tile_height = 43)

# Add the Group to the Display
group = displayio.Group(scale=3)

# Add the sprite to the Group
group.append(sprite)

HAL.main_splash().append(group)

# Set sprite location
HAL.main_splash().x = 100
HAL.main_splash().y = 45


def run_example():
    # Loop through each sprite in the sprite sheet
    source_index = 0
    walk_offset = 0
    while True:
        sprite[0] = (source_index % 4) + walk_offset
        source_index = (source_index + 1) % 4
        if source_index is 0:
            walk_offset = (walk_offset + 4) % 16
        time.sleep(.15)
