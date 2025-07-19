class PanelNavigationMixin:
    def __init__(self):
        self.selected_index = 0

    def flatten_keys(self, options):
        """Flattens a 2D list into a 1D list of keys"""
        return options[0] + options[1]

    def move_selection_up(self, options):
        if self.selected_index > 0:
            self.selected_index -= 1
            return True
        return False

    def move_selection_down(self, options):
        total = len(self.flatten_keys(options))
        if self.selected_index < total - 1:
            self.selected_index += 1
            return True
        return False

    def split_for_columns(self, lines, left_count):
        """Splits lines into left/right columns given left column line count"""
        left = lines[:left_count]
        right = lines[left_count:]
        return left, right

    def apply_marker(self, *, left_lines, right_lines, selected_index):
        total_left = len(left_lines)
        if 0 <= selected_index < total_left:
            left_lines[selected_index] = "> " + left_lines[selected_index]
        elif total_left <= selected_index < total_left + len(right_lines):
            idx = selected_index - total_left
            right_lines[idx] = "> " + right_lines[idx]
