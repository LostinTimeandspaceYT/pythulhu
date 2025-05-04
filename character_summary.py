from text_viewport import TextViewport
import displayio

class CharacterSummaryPanel:
    def __init__(self, character, x=10, y=10, width=300, height=160, max_lines=10):
        self.character = character
        self.group = displayio.Group()
        self.viewport = TextViewport(
            x=x,
            y=y,
            width=width,
            height=height,
            max_lines=max_lines,
            line_height=14,
            show_background=True,
            background_color=0x222222
        )
        self.group.append(self.viewport.group)

    def update(self):
        lines = self.character.render_summary_lines(max_lines=self.viewport.max_lines)
        self.viewport.set_lines(lines)

    def show(self, hal):
        self.update()
        hal.root_group.append(self.group)

    def clear(self):
        self.viewport.set_lines([])

    def hide(self, hal):
        if self.group in hal.root_group:
            hal.root_group.remove(self.group)