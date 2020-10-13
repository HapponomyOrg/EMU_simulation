from enum import Enum


class Interval(Enum):
    DAY = 0
    WEEK = 1
    MONTH = 2
    YEAR = 3


class Period:
    WEEK_DAYS: int = 7
    MONTH_DAYS: int = 28
    YEAR_DAYS: int = 336

    def __init__(self, length: int, interval: Interval):
        self.__length: int = length
        self.__interval: Interval = interval

        if self.interval == Interval.DAY:
            self.__days = length
        elif self.interval == Interval.WEEK:
            self.__days = length * self.WEEK_DAYS
        elif self.interval == Interval.MONTH:
            self.__days = length * self.MONTH_DAYS
        else:
            self.__days = length * self.YEAR_DAYS

    @property
    def length(self) -> int:
        return self.__length

    @property
    def interval(self) -> Interval:
        return self.__interval

    @property
    def days(self) -> int:
        return self.__days

    def period_complete(self, cycle: int) -> bool:
        return (cycle + 1) % self.days == 0
