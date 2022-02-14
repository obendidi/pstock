import typing as tp
from datetime import date, datetime

from pstock.utils.utils import parse_datetime


class Timestamp(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: tp.Union[str, int, float, date, datetime]) -> int:
        return parse_datetime(value).int_timestamp


class ReadableResponse(tp.Protocol):
    def read(self) -> tp.Union[str, bytes]:
        ...
