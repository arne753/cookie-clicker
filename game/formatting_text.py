def yellow_format_text(text: str) -> str:
    return f"\033[38;2;255;183;34m{text}\033[0m"


def red_format_text(text: str) -> str:
    return f"\033[31m{text}\033[0m"


def blue_format_text(text: str) -> str:
    return f"\033[34m{text}\033[0m"


def cyan_format_text(text: str) -> str:
    return f"\033[36m{text}\033[0m"


def magenta_format_text(text: str) -> str:
    return f"\033[35m{text}\033[0m"


def black_format_text(text: str) -> str:
    return f"\033[30m{text}\033[0m"
