from enum import Enum

class Color(Enum):
    RED = 31
    PUPLE = 95
    CYAN = 96
    DARK_CYAN = 36
    BLUE = 94
    GREEN = 92
    YELLOW = 93

def colorize(text, color):
    """return text in the specified color."""
    if color not in Color:
        raise KeyError(f'Invalid text color: {color}')
    
    return f'\033[{color.value}m{text}\033[0m'