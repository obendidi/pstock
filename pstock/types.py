import typing as tp

# from datetime import datetime

# from pstock.core.times import parse_datetime


# class TimeStamp(int):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, value: tp.Union[str, int, float, datetime]) -> int:
#         return parse_datetime(value).int_timestamp


class ReadableResponse(tp.Protocol):
    def read(self) -> tp.Union[str, bytes]:
        ...
