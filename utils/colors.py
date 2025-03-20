from typing import List, Tuple
import re
import curses

ANSI_PATTERN = re.compile(r'\x1b\[([0-9;]+)m')

# Mapeamento de cores ANSI para curses
ANSI_COLORS_FORE = {
    '30': curses.COLOR_BLACK, '31': curses.COLOR_RED, '32': curses.COLOR_GREEN, '33': curses.COLOR_YELLOW,
    '34': curses.COLOR_BLUE, '35': curses.COLOR_MAGENTA, '36': curses.COLOR_CYAN, '37': curses.COLOR_WHITE,
    '90': curses.COLOR_BLACK + 8, '91': curses.COLOR_RED + 8, '92': curses.COLOR_GREEN + 8, '93': curses.COLOR_YELLOW + 8,
    '94': curses.COLOR_BLUE + 8, '95': curses.COLOR_MAGENTA + 8, '96': curses.COLOR_CYAN + 8, '97': curses.COLOR_WHITE + 8,
}

ANSI_COLORS_BACK = {
    '40': curses.COLOR_BLACK, '41': curses.COLOR_RED, '42': curses.COLOR_GREEN, '43': curses.COLOR_YELLOW,
    '44': curses.COLOR_BLUE, '45': curses.COLOR_MAGENTA, '46': curses.COLOR_CYAN, '47': curses.COLOR_WHITE,
    '100': curses.COLOR_BLACK + 8, '101': curses.COLOR_RED + 8, '102': curses.COLOR_GREEN + 8, '103': curses.COLOR_YELLOW + 8,
    '104': curses.COLOR_BLUE + 8, '105': curses.COLOR_MAGENTA + 8, '106': curses.COLOR_CYAN + 8, '107': curses.COLOR_WHITE + 8,
}

def parse_ansi(text: str) -> List[Tuple[str, int]]:
    """Remove códigos ANSI e retorna uma lista de (texto, atributo)."""
    parsed: List[Tuple[str, int]] = []
    current_foreground = -1  # -1 indica uso da cor padrão
    current_background = -1
    current_attr = curses.A_NORMAL

    pos = 0
    for match in ANSI_PATTERN.finditer(text):
        # Adiciona o texto entre as sequências ANSI
        if match.start() > pos:
            parsed.append((text[pos:match.start()], current_attr))
        pos = match.end()

        # Processa os códigos ANSI
        codes = match.group(1).split(';')
        for code in codes:
            if code == '0':  # Reset
                current_foreground = -1
                current_background = -1
                current_attr = curses.A_NORMAL
            elif code in ANSI_COLORS_FORE:
                current_foreground = ANSI_COLORS_FORE[code]
            elif code in ANSI_COLORS_BACK:
                current_background = ANSI_COLORS_BACK[code]

        # Criar um par de cores único para o foreground/background
        if current_foreground != -1 or current_background != -1:
            pair_id = (current_foreground + 1) * 10 + (current_background + 1)
            curses.init_pair(pair_id, current_foreground, current_background)
            current_attr = curses.color_pair(pair_id)

    # Adiciona qualquer texto restante
    if pos < len(text):
        parsed.append((text[pos:], current_attr))

    return parsed

def AddStyledStr(stdscr: curses.window, text: str):
    curses.start_color()
    curses.use_default_colors()

    parsed_text = parse_ansi(text)

    y, x = stdscr.getyx()
    for part, attr in parsed_text:
        stdscr.addstr(y, x, part, attr)
        x += len(part)

    stdscr.refresh()
