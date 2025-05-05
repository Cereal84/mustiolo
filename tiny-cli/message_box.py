from enum import IntEnum
from typing import List

TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_LEFT = 2
BOTTOM_RIGHT = 3
TOP = 4
SIDE = 5


_borders = []
_borders.append(['', '', '', '', '', '']) # 0 NOBORDER
_borders.append(['╭', '╮', '╰', '╯', '─', '│']) # 1 SINGLE_ROUNDED
_borders.append(['┌', '┐', '└', '┘', '─', '│']) # 2 SINGLE_RECTANGLE
_borders.append(['┏', '┓', '┗', '┛', '━', '┃']) # 3 SINGLE_BOLD
_borders.append(['╔', '╗', '╚', '╝', '═', '║']) # 4 DOUBLE_RECTANGLE

class BorderStyle(IntEnum):
    """Enum for border styles."""
    NONE = 0
    SINGLE_ROUNDED = 1
    SINGLE_RECTANGLE = 2
    SINGLE_BOLD = 3
    DOUBLE_RECTANGLE = 4


def _handle_line(line: str, border_style: BorderStyle, columns: int = 80) -> List[str]:
    """Handle a line of text, wrapping it to fit within the specified number of columns."""

    side_border = _borders[border_style][SIDE]
    message_spaces = columns - ((len(side_border) * 2) + 2)
    if message_spaces >= len(line):
        return [f"{line}{' '*(message_spaces - len(line))}"]

    # we need to split the line into chunks of message_spaces
    lines_num = len(line) // message_spaces
    lines = []
    processed_chars = 0
    for i in range(lines_num + 1):
        if i == lines_num:
            lines.append(f"{line[processed_chars:]}{' '*(message_spaces - (len(line[processed_chars:])))}")
        else:
            lines.append(line[processed_chars:processed_chars + message_spaces])
            processed_chars += message_spaces

    return lines


def draw_message_box(title: str, content: str, border_style: BorderStyle = BorderStyle.SINGLE_ROUNDED,
                     columns: int = 80) -> str:
    """Draw a message box with the given title and content.
    
                ╭──────── Title ────────╮
                │    CONTENT            │
                ╰───────────────────────╯
    """
    borders = _borders[border_style]
    # header
    header_fill = columns - (len(title) + len(borders[TOP_LEFT]) + len(borders[TOP_RIGHT]) + 2) # 2 whitespaces
    half_header_fill = header_fill // 2
    box = f"{borders[TOP_LEFT]}{borders[TOP]* half_header_fill} {title} {borders[TOP] * (half_header_fill + header_fill%2)}{borders[TOP_RIGHT]}"

    # content will be split into lines
    # and each line will be wrapped to fit within the specified number of columns.
    for line in content.splitlines():
        for chunk in _handle_line(line, border_style, columns):
            box += f"\n{borders[SIDE]} {chunk} {borders[SIDE]}"
    # footer
    box += f"\n{borders[BOTTOM_LEFT]}{borders[TOP] * (columns - 2)}{borders[BOTTOM_RIGHT]}"
    return box
