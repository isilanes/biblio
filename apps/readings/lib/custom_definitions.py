from enum import Enum


class ReadingStatus(int, Enum):
    """
    Enum for different statuses in which a Reading can be:
    - STARTED: Reading is ongoing.
    - COMPLETED: Reading was finished, reading until the end of the book.
    - DNF: did not finish. Left the book before completing it.
    """
    STARTED = 1
    COMPLETED = 2
    DNF = 3

    @classmethod
    def get_choices(cls) -> list:
        return [(v.value, v.name) for v in cls]
