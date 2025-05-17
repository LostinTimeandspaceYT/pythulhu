import displayio
from ui_context import UIContext

class BasePanel:
    def __init__(self, context: UIContext):
        self.context = context
        self.hal = context.hal
        self.manager = context.manager
        self.character = context.character
        self.group = displayio.Group()
        self.mode = "select"  # or "edit"
        self.awaiting_release = False

    def show(self):
        self.hal.clear_display()
        self.hal.reset_display()
        self.hal.root_group.append(self.group)

    def hide(self):
        if self.group in self.hal.root_group:
            self.hal.root_group.remove(self.group)

    def attach_to(self):
        if self.group not in self.hal.root_group:
            self.hal.root_group.append(self.group)

    def detach_from(self):
        if self.group in self.hal.root_group:
            self.hal.root_group.remove(self.group)

    def toggle_mode(self):
        self.mode = "edit" if self.mode == "select" else "select"

    def render_option_labels(self, labels, start_y: int, selected_index: int, param_keys: list[str], param_values: dict[str, any]):
        y = start_y
        for i, key in enumerate(param_keys):
            if self.mode == "select":
                prefix = "> " if i == selected_index else "  "
            else:  # edit mode
                prefix = "* " if i == selected_index else "  "
            labels[i + 1].text = f"{prefix}{key}: {param_values[key]}"
            labels[i + 1].y = y
            y += 20

    def on_mode_change(self):
        """Override in child classes"""
        pass

    def reset(self, **kwargs):
        """Override in child classes"""
        pass

    def update(self):
        if self.hal.is_button_pressed():
            if not self.awaiting_release:
                self.toggle_mode()
                self.on_mode_change()
                self.awaiting_release = True
        else:
            self.awaiting_release = False

