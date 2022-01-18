from pydantic import BaseModel

import typing as tp

from pstock.schemas.base import BaseDataFrameModel


class Earning(BaseModel):

    quarter: str
    estimate: float
    actual: float
    revenue: float
    earnings: float


class Earnings(BaseDataFrameModel):
    __root__: tp.List[Earning]
