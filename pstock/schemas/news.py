import datetime
import typing as tp

import pandas as pd
from pydantic import BaseModel, Field

from pstock.schemas.base import BaseDataFrameModel


class Publication(BaseModel, allow_population_by_field_name=True):
    date: datetime.datetime
    title: str
    url: str = Field(alias="link")
    summary: tp.Optional[str]


class News(BaseDataFrameModel):
    __root__: tp.List[Publication]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self._convert_to_df(index_column="date", sort_index=True)
        return self._df
