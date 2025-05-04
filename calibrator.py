import terminalio
import time
from displayio import Group
from adafruit_display_text import label
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect

class Calibrator:
    def __init__(self, tsc, screen_width=320, screen_height=240):
        self.tsc = tsc
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw_crosshair(self, group, x, y, size=10, color=0xFFFF00):
        h_line = Line(x - size, y, x + size, y, color=color)
        v_line = Line(x, y - size, x, y + size, color=color)
        group.append(h_line)
        group.append(v_line)

    def calibrate(self, display=None):
        corners = [
            ("top-left", 20, 20),
            ("top-right", self.screen_width - 20, 20),
            ("bottom-left", 20, self.screen_height - 20),
            ("bottom-right", self.screen_width - 20, self.screen_height - 20),
        ]

        raw_xs = []
        raw_ys = []

        for name, screen_x, screen_y in corners:
            if display:
                display.clear_display()
                group = Group()
                self.draw_crosshair(group, screen_x, screen_y)

                # Adjust text position based on corner to keep it visible
                text_x = screen_x + 10 if screen_x < self.screen_width // 2 else screen_x - 90
                text_y = screen_y + 20 if screen_y < self.screen_height // 2 else screen_y - 30

                text = label.Label(
                    terminalio.FONT,
                    text=f"Touch {name}\n(Hold 1s)",
                    color=0xFFFFFF,
                    x=text_x,
                    y=text_y
                )
                group.append(text)
                display.root_group.append(group)
            print(f"Waiting for touch at {name}...")

            while not self.tsc.touched:
                pass

            samples = []
            for _ in range(10):
                if self.tsc.touched:
                    point = self.tsc.touch
                    samples.append((point["x"], point["y"]))
                time.sleep(0.05)

            avg_x = sum(p[0] for p in samples) // len(samples)
            avg_y = sum(p[1] for p in samples) // len(samples)
            print(f"{name}: avg_x={avg_x}, avg_y={avg_y}")

            raw_xs.append(avg_x)
            raw_ys.append(avg_y)

            while self.tsc.touched:
                pass

        # Assign calibrated bounds
        self.raw_min_x = min(raw_xs)
        self.raw_max_x = max(raw_xs)
        self.raw_min_y = min(raw_ys)
        self.raw_max_y = max(raw_ys)

        # Auto-correct inverted bounds
        if self.raw_min_x > self.raw_max_x:
            self.raw_min_x, self.raw_max_x = self.raw_max_x, self.raw_min_x
        if self.raw_min_y > self.raw_max_y:
            self.raw_min_y, self.raw_max_y = self.raw_max_y, self.raw_min_y

        print("Calibration complete.")
        print(f"X: {self.raw_min_x} - {self.raw_max_x}")
        print(f"Y: {self.raw_min_y} - {self.raw_max_y}")

        return {
            "raw_min_x": self.raw_min_x,
            "raw_max_x": self.raw_max_x,
            "raw_min_y": self.raw_min_y,
            "raw_max_y": self.raw_max_y
        }
