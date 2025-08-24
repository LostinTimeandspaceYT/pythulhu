# Pythulhu

Electronic dice roller and character sheet interface for TTRPGs.

## Features

- Support for multiple game systems
- Save and load files via a micro-SD card
- Boasts a "Large" 2.8 inch display with touch controls
- Rotary Encoder with push button

## Games Supported

See Game road map below

- Call of Cthulhu 7th edition
  - Pulp Cthulhu
- ~~Cyberpunk Red~~ (After CoC is complete)

## Road Maps

Check here to see if your TTRPG of choice is supported and what features are coming down the pipeline.

### Call of Cthulhu

Features:

- [x] Loads character sheets via `JSON`.
- [x] Make skill rolls
- [x] Make charactertisic rolls
- [x] Marks skills for improvement
- [x] Added Panel for handling sanity rolls
- [x] Added Logic to save character on exit.
- [x] Created panel for selecting equipped weapon
- [x] Add panel for development phase
- [x] Add panel for handling combat

Future Updates:

- [ ] Add Movement Rate
- [ ] Add Logic to deal with injuries and insanity flags
- [ ] Add panel for inventory management

### Pulp Cthulhu

- [ ] Add panel to check Talents
- [ ] Incorporate Talents into game logic


## Libraries & Dependencies

This project uses CircuitPython v9.x.x

- `adafruit_button`
- `adafruit_display_text`
- `adafruit_display_shapes`
- `adafruit_sdcard`
- `adafruit_seesaw`
- `adafruit_tsc2007`
- `adafruit_ili9341`
- `adafruit_imageload`
- `neopixel`

## Hardware Used

[Adafruit Metro RP2350 with PSRAM](https://www.adafruit.com/product/6267)
Upgrade from original RP2040 edition. PSRAM is optional, but can decrease load
times if working with large images.

[2.8" TFT Touch Shield](https://www.adafruit.com/product/1651)
Capactive touch screen is also an option, though it is not currently supported

[I2C Stemma QT Encoder Breakout](https://www.adafruit.com/product/5880)
For fine-grained user controls.

[Stemma-QT to Stemma-QT cable:](https://www.adafruit.com/product/4399):
Connects the encoder to the main board.

## Putting it together

### Hardware Setup

1. Connect the TFT Touch Shield to the Metro, ensuring all the pins are fully seated

> [!caution]
> Be careful to align the back 6 GPIO pins during installation

2. Connect one end of the Stemma-QT cable to one of the connectors on the encoder.
Doesn't matter which one you choose.

> [!note]
> Adventerous developers could add support for additional Encoders.

3. Connect the other end of the Stemma-QT cable to the connector on the Metro.

> [!note]
> This is near the USB-C connector and reset button.

4. Follow the SD Card set up below. Once complete insert the SD card into the slot on the Metro.

### SD Card set up

> [!note]
> TODO: Package dependencies in future release

- clone the repo
- install circuit python version 9.x.x onto Metro
- copy dependencies to Metro (see above)
- copy contents of repo (images are optional) to Metro


## Software Architecture

### Hardware related

**HAL:**
Hardware Abstraction Layer.

**FileManager:**
Handles file IO (JSON, BMPs).
Characters and images are considered `assets` and the follow a known file structure.

**UIContext:**
Handles UI display buffers with panel caching

**TouchManager:**
Handles touch controls needed for `TouchButton` classes

### Game Logic

**GameFactory:**
Lets users pick the game + character they want to play.
Developers can register new games into the following dict:

```py
GAMES = {
    "call_of_cthulhu": CthulhuGame,
    "pulp_cthulhu": CthulhuGame,
  # "your_game_here": MyGame,
}
```

**GameRunner:**
runs game event loop

**Game (e.g. CthulhuGame):**
Owns `PanelPool`, game logic, and interprets dice roll logic.

**Dice:**
Rolls dice. Dice are tuples `(num_dice, num_sides)`.
This conforms to the typical `1d20`, `4d6` nomenclature TTRPGs use.
Games can extend this class to add functionality tailored for their needs.

See `CthulhuGame` for examples

**RollResult:**
A monad-like wrapper for games to display roll results.
`stylize()` can be used to color text or change pixel colors.

### UI Elements

**PanelPool:**
Game-specific panels, registered to the `UIContext`.
Panels can regiser factory functions to the pool for dynamic dispatch

**BasePanel:**
Provides basic functionality to panels such as a user selection mode via the encoder.
By pushing the button on the encoder, the user can enter either `select` or `edit` mode.

- select: `>`
- edit: `*`

**PanelNavigationMixin:**
Provides Navigiation support via the encoder wheel.
By rotating the wheel, users can traverse lists of options, such as a PCs skills.
Also provides helper method for splitting long lists into two columns.

Other example panels are provided in `panels/`.

## Additional Information

### Chaosium's Fan Material Policy  

“This application uses trademarks and/or copyrights owned by Chaosium Inc/Moon Design Publications LLC, which are used under Chaosium Inc’s Fan Material Policy.
We are expressly prohibited from charging you to use or access this content. This application is not published, endorsed, or specifically approved by Chaosium Inc.
For more information about Chaosium Inc’s products, please visit [www.chaosium.com](www.chaosium.com).”

[Link](https://www.chaosium.com/fan-material-policy/)
