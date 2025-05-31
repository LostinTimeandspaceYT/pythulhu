# Pythulhu

*An electronic dice roller and character sheet interface for Call of Cthulhu and Pulp Cthulhu 7th edition*

This project uses CircuitPython v9.x.x

## Libraries & Dependencies

- `adafruit_button`
- `adafruit_display_text`
- `adafruit_display_shapes`
- `adafruit_sdcard`
- `adafruit_seesaw`
- `adafruit_tsc2007`
- `adafruit_ili9341`
- `adafruit_imageload`
- `neopixel`

More to come in the following months:

## Hardware Used

Main Board: [Adafruit Metro RP2040](https://www.adafruit.com/product/5786)

Display: [2.8" TFT Touch Shield](https://www.adafruit.com/product/1651)

Encoder: [I2C Stemma QT Encoder Breakout](https://www.adafruit.com/product/5880)

Stemma-QT to Stemma-QT cable


## Software Architecture

[ FileManager ]         -- handles file IO (JSON, images)

↓
     
[ UIContext ]           -- manages display, touch input, LEDs, and encoder

↓
     
[ GameFactory ]         -- lets user pick game + character

↓
     
[ GameRunner ]          -- runs one game, manages UIContext + main loop

↓
     
[ Game (e.g. CthulhuGame) ] -- owns PanelPool, game logic, roll logic

↓
     
[ PanelPool ]           -- game-specific panel reuse

## Chaosium's Fan Material Policy  

“This application uses trademarks and/or copyrights owned by Chaosium Inc/Moon Design Publications LLC, which are used under Chaosium Inc’s Fan Material Policy.
We are expressly prohibited from charging you to use or access this content. This application is not published, endorsed, or specifically approved by Chaosium Inc.
For more information about Chaosium Inc’s products, please visit [www.chaosium.com].”

[Link:](https://www.chaosium.com/fan-material-policy/)
