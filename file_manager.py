import os
import busio
import digitalio
import board
import storage
import adafruit_sdcard

MOUNT_POINT: str = "/sd"
CHARACTER_PATH: str = MOUNT_POINT + "/characters/"
IMAGES_PATH: str = MOUNT_POINT + "/assets/images/"

class FileManager:

    @classmethod
    def mount_sdcard(cls):
        # Connect to the card and mount the filesystem.
        spi = busio.SPI(board.SD_SCK, board.SD_MOSI, board.SD_MISO)
        cs = digitalio.DigitalInOut(board.SD_CS)
        sdcard = adafruit_sdcard.SDCard(spi, cs)
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, MOUNT_POINT)

    @classmethod
    def write_to(cls, path: str, contents: str):
        with open(path, "a") as f:
            f.write(contents)
        # file is saved when with goes out of scope

    @classmethod
    def get_character_path(cls, game: str, character_name: str) -> str:
        return CHARACTER_PATH + game + "/" + character_name + ".json"

    @classmethod
    def list_characters(cls, game: str) -> list[str]:
        fpath = CHARACTER_PATH + game
        return [pc[:-5] for pc in os.listdir(fpath) if pc.endswith(".json")]

    @classmethod
    def character_exists(cls, game: str, name: str) -> bool:
        return os.path.exists(cls.get_character_path(game, name))

    @classmethod
    def list_all_character_paths(cls, game: str):
        fpath = CHARACTER_PATH + game
        for pc in os.listdir(fpath):
            yield pc

    @classmethod
    def get_image_path(cls, image_name: str) -> str:
        return IMAGES_PATH + image_name + ".bmp"


    # This helper function will print the contents of the SD
    # Taken from the adafruit examples
    # src: https://learn.adafruit.com/adafruit-metro-rp2040/sd-card
    @classmethod
    def print_directory(cls, path: str, tabs=0):
        for file in os.listdir(path):
            stats = os.stat(path + "/" + file)
            isdir = stats[0] & 0x4000
            prettyprintname = ""
            for _ in range(tabs):
                prettyprintname += "   "
            prettyprintname += file
            if isdir:
                prettyprintname += "/"
            print("{0:<40}".format(prettyprintname))

            # recursively print directory contents
            if isdir:
                cls.print_directory(path + "/" + file, tabs + 1)
