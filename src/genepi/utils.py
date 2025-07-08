from typing import Any, ClassVar

from typing_extensions import Self


def timecode_to_seconds(timecode: str) -> int:
    parts = timecode.split(":")
    factor = 1
    total = 0
    for part in reversed(parts[-3:]):
        total += int(part) * factor
        factor *= 60
    return total


def seconds_to_timecode(seconds: int | float) -> str:
    millis = seconds - int(seconds)
    h, m = divmod(int(seconds), 3600)
    m, s = divmod(m, 60)
    s = s + millis
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def bytes_to_mb(size: int) -> str:
    size = size / 1024 / 1024
    return f"{size:.2f}Mb"


class Singleton(type):
    _instances: ClassVar[dict] = {}

    def __call__(cls, *args: tuple, **kwargs: dict[str, Any]) -> Self:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
