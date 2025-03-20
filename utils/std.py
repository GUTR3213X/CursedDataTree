import curses
from . import colors

class Input:
    def __init__(self, window: curses.window):
        self.window = window
    def __call__(self, prompt: str):
        colors.AddStyledStr(self.window, prompt)
        self.window.refresh()
        curses.echo()
        curses.curs_set(1)
        user_input = self.window.getstr().decode('utf-8')
        curses.noecho()
        return user_input

class Print:
    def __init__(self, window: curses.window) -> None:
        self.window = window
    def __call__(self, *strings: str, sep: str = ' ', end: str = '\n'):
        joined_str = sep.join(strings)
        for line in joined_str.split('\n'):
            colors.AddStyledStr(self.window, f'{line}\n')
        self.window.refresh()