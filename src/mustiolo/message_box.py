from enum import IntEnum
from typing import List


TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_LEFT = 2
BOTTOM_RIGHT = 3
TOP = 4
SIDE = 5


_borders : List[List[str]]= [
   ['', '', '', '', '', ''], # 0 NOBORDER
   ['╭', '╮', '╰', '╯', '─', '│'], # 1 SINGLE_ROUNDED
   ['┌', '┐', '└', '┘', '─', '│'], # 2 SINGLE_RECTANGLE
   ['┏', '┓', '┗', '┛', '━', '┃'], # 3 SINGLE_BOLD
   ['╔', '╗', '╚', '╝', '═', '║'], # 4 DOUBLE_RECTANGLE
]

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

    # convert '\t' to '    ' (4 spaces)
    line = line.expandtabs(4)

    # Calculate the number of spaces available for the message removing the borders and padding
    message_spaces = columns - ((len(side_border) * 2) + 2)
    # Split the line into chunks of message_spaces
    lines = [line[i:i + message_spaces] for i in range(0, len(line), message_spaces)]
    # Pad the last line if necessary
    if len(lines) == 0:
        return [f"{' ' * message_spaces}"]

    if len(lines[-1]) < message_spaces:
        lines[-1] += ' ' * (message_spaces - len(lines[-1]))
    return lines


def draw_message_box(title: str, content: str, border_style: BorderStyle = BorderStyle.SINGLE_ROUNDED,
                     columns: int = 80) -> str:
    """
    Draw a message box with the given title and content.

    Args:
        title (str): The title of the message box.
        content (str): The content inside the message box.
        border_style (BorderStyle): The style of the border.
        columns (int): The width of the message box.

    Returns:
        str: The formatted message box as a string.

    Example:
        >>> print(draw_message_box("Title", "Content", BorderStyle.SINGLE_RECTANGLE, 30))
        ┌────── Title ──────┐
        │ Content           │
        └───────────────────┘
    """

    # check if the title fits within the specified number of columns
    # otherwise use sub string
    if len(title) + 4 > columns:
        title = title[:columns - 4]

    borders = _borders[border_style]
    lines = []

    if title != "":
        # header with title
        header_fill = columns - (len(title) + len(borders[TOP_LEFT]) + len(borders[TOP_RIGHT]) + 2) # 2 whitespaces
        half_header_fill = header_fill // 2
        lines.append(
            f"{borders[TOP_LEFT]}{borders[TOP]* half_header_fill} {title} {borders[TOP] * (half_header_fill + header_fill%2)}{borders[TOP_RIGHT]}"
        )
    else:
        # header with title
        header_fill = columns - (len(borders[TOP_LEFT]) + len(borders[TOP_RIGHT]))
        lines.append(
            f"{borders[TOP_LEFT]}{borders[TOP]* header_fill}{borders[TOP_RIGHT]}"
        )

    # content will be split into lines
    # and each line will be wrapped to fit within the specified number of columns.
    for line in content.splitlines():
        for chunk in _handle_line(line, border_style, columns):
            lines.append(f"{borders[SIDE]} {chunk} {borders[SIDE]}")
    # footer
    lines.append(f"{borders[BOTTOM_LEFT]}{borders[TOP] * (columns - 2)}{borders[BOTTOM_RIGHT]}")
    return '\n'.join(lines)