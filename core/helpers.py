from enum import StrEnum, auto
from typing import NamedTuple

class AvailableActon(NamedTuple):
    action: str
    color: str
    text: str


class Perms(StrEnum):
    CAN_VIEW_PRICES = auto()
    CAN_VIEW_BALANCE = auto()

    CAN_VIEW_TWITCH_ORDERS = auto()
    CAN_CREATE_TWITCH_ORDERS = auto()
    
    CAN_VIEW_YOUTUBE_ORDERS = auto()
    CAN_CREATE_YOUTUBE_ORDERS = auto()
    ACTIVE = auto()
    REJECTED = auto()
    STOPPED = auto()
    NOT_STARTED = auto()
    WAITING = auto()
    DELAY = auto()
    OFFLINE = auto()
    CANCELED = auto()
    NOT_PAID = auto()
    PAID = auto()
    CLOSED = auto()
    ONLINE_LIMIT_IS_REACHED = "online_limit"
    ERROR = auto()
    SUSPENDED = auto()


class Platform(StrEnum):
    TWITCH = auto()
    YOUTUBE = auto()
    GOODGAME = auto()
    TROVO = auto()
    VKPLAY = auto()

    @staticmethod
    def enabled_platforms() -> tuple:
        return Platform.TWITCH, Platform.YOUTUBE


class OrderStatus(StrEnum):
    NOT_SYNCHRONIZED = auto()
    ACTIVE = auto()
    REJECTED = auto()
    STOPPED = auto()
    NOT_STARTED = auto()
    WAITING = auto()
    DELAY = auto()
    OFFLINE = auto()
    CANCELED = auto()
    NOT_PAID = auto()
    PAID = auto()
    CLOSED = auto()
    ONLINE_LIMIT = auto()
    ERROR = auto()
    SUSPENDED = auto()


class TaskAction(StrEnum):
    RUN = auto()
    CANCEL = auto()
    STOP = auto()
    CHANGE_ONLINE = "change:online"
    INCREASE_ON = "increase:on"
    INCREASE_OFF = "increase:off"
    CHANGE_INCREASE_VALUE = "change:increase:value"
    ADD_VIEWS = "add:views"
    TWITCH_STREAM = "twitch:stream"
    YOUTUBE_STREAM = "youtube:stream"
