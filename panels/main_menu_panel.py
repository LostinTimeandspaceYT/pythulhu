from panels.base_panel import BasePanel
from touch_ui import LightTouchButton

class MainMenuPanel(BasePanel):
	def __init__(self, context):
		super().__init__(context)

		self.buttons = [
			LightTouchButton("quit", 50, 120, 220, 30, "Quit", callback=self.quit_game)
		]
		for btn in self.buttons:
			btn.attach_to(self.group)


	def add_button(self, button):
		self.buttons.insert(0, button)
		button.attach_to(self.group)

	def add_buttons(self, buttons):
		"""To permit games to customize their menus"""
		for btn in buttons:
			self.buttons.insert(0, btn)
			btn.attach_to(self.group)

	def attach_to(self):
		super().attach_to()
		for btn in self.buttons:
			btn.register(self.context.manager)
		self.context.show_nav_button("back", callback=self.quit_game)
		self.context.hide_nav_button("next")
		self.context.hide_nav_button("prev")

	def detach_from(self):
		super().detach_from()
		for btn in self.buttons:
			btn.unregister(self.context.manager)


	def quit_game(self, button=None):
		self.context.should_exit = True
