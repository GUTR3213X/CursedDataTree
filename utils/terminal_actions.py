from typing import Callable, Any
import curses


ignore = type['ignore']

class Action:
    def __init__(self, keyNC: tuple[str, int | ignore] | str, desc: str, *functions: Callable[..., Any]) -> None:
        if isinstance(keyNC, tuple):
            self.keyname = keyNC[0]
            self.keycode = keyNC[1]
        else:
            self.keyname = keyNC
            self.keycode = ord(keyNC) if keyNC != '' else ignore
        self.desc = desc
        self.functions = functions
    def __str__(self):
        return f'[{self.keyname:^5}] {self.desc}'
    def __call__(self):
        return [function() for function in self.functions]
class Actions:
    def __init__(self, window: curses.window):
        self.window = window
    def get(self, *actions: Action, keycode: int):
        for action in actions:
            if action.keycode in (keycode, ignore):
                return action()
        raise KeyError(f'Tecla inválida: {keycode}("{chr(keycode)}")')
    def show(self, *actions: Action):
        for action in actions:
            self.window.addstr(f'{action}\n')
    def request_key(self):
        curses.cbreak()
        curses.noecho()
        keycode = self.window.getch()
        curses.echo()
        curses.nocbreak()
        return keycode
    def display(self, *actions: Action):
        def wrapper():
            self.show(*actions)
            curses.curs_set(0)
            keycode = self.request_key()
            curses.curs_set(1)
            return self.get(*actions, keycode=keycode)
        return wrapper
    def display_loop(self, *actions: Action):
        def wrapper():
            curses.init_pair(1, curses.COLOR_RED, -1)
            self.show(*actions)
            y, _ = self.window.getyx()
            while True:
                try:
                    keycode = self.request_key()
                    return self.get(*actions, keycode=keycode)
                except KeyError as e:
                    self.window.addstr(y, 0, f'{e}\n', curses.color_pair(1))
        return wrapper
