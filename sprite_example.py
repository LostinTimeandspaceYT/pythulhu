# SPDX-FileCopyrightText: 2019 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import displayio
from hardware import HAL

def run_example():
    my_sprite = HAL.create_sprite("example", 43, 43)

    # Add the Group to the Display
    group = displayio.Group(scale=3)
    group.append(my_sprite)

    # Set sprite location
    group.x = 100
    group.y = 45

    HAL.main_splash().append(group)
    # Loop through each sprite in the sprite sheet
    source_index = 0
    walk_offset = 0
    while True:
        my_sprite[0] = source_index + walk_offset
        source_index = (source_index + 1) % 4

        if source_index is 0:
            walk_offset = (walk_offset + 4) % 16

        time.sleep(.15)
