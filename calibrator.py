import time
import terminalio
from displayio import Group
from adafruit_display_text import label
from adafruit_display_shapes.line import Line

class Calibrator:
    def __init__(self, tsc, screen_width=320, screen_height=240):
        self.tsc = tsc
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw_crosshair(self, group, x, y, size=10, color=0xFFFF00):
        """Draw a crosshair at the target point."""
        group.append(Line(x - size, y, x + size, y, color=color))
        group.append(Line(x, y - size, x, y + size, color=color))

    def sample_touch(self, num_samples=10, delay=0.05):
        """Collect and average multiple touch samples."""
        samples = []
        while len(samples) < num_samples:
            if self.tsc.touched:
                point = self.tsc.touch
                if point:
                    samples.append((point["x"], point["y"]))
            time.sleep(delay)
        avg_x = sum(p[0] for p in samples) // len(samples)
        avg_y = sum(p[1] for p in samples) // len(samples)
        return avg_x, avg_y

    def wait_for_touch(self):
        """Block until a touch is detected."""
        while not self.tsc.touched:
            time.sleep(0.01)

    def wait_for_release(self):
        """Block until the screen is released."""
        while self.tsc.touched:
            time.sleep(0.01)

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
            print(f"Waiting for touch at {name}...")

            if display:
                group = Group()
                self.draw_crosshair(group, screen_x, screen_y)

                # Place text near the corner, offset to avoid occlusion
                text_x = screen_x + 10 if screen_x < self.screen_width // 2 else screen_x - 100
                text_y = screen_y + 20 if screen_y < self.screen_height // 2 else screen_y - 30
                prompt = label.Label(
                    terminalio.FONT,
                    text=f"Touch {name}\nand hold...",
                    color=0xFFFFFF,
                    x=text_x,
                    y=text_y
                )
                group.append(prompt)

                # Replace root_group content
                display.root_group = group

            self.wait_for_touch()
            avg_x, avg_y = self.sample_touch()
            print(f"{name}: avg_x={avg_x}, avg_y={avg_y}")

            raw_xs.append(avg_x)
            raw_ys.append(avg_y)

            self.wait_for_release()
            time.sleep(0.3)

        # Assign min/max with auto-flip correction
        self.raw_min_x = min(raw_xs)
        self.raw_max_x = max(raw_xs)
        self.raw_min_y = min(raw_ys)
        self.raw_max_y = max(raw_ys)

        print("Calibration complete:")
        print(f"  X: {self.raw_min_x} - {self.raw_max_x}")
        print(f"  Y: {self.raw_min_y} - {self.raw_max_y}")

        return {
            "raw_min_x": self.raw_min_x,
            "raw_max_x": self.raw_max_x,
            "raw_min_y": self.raw_min_y,
            "raw_max_y": self.raw_max_y
        }
