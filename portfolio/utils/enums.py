from enum import Enum


class RUN_MODE(Enum):
    NORMAL, RETRY, RELOAD = range(2)


class INSTRUMENT_STATUS(Enum):
    OPEN, PENDING_CLOSE, CLOSED = range(3)
