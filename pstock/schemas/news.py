import datetime
from pydantic import BaseModel, Field
from pstock.schemas.base import BaseDataFrameModel
import typing as tp
import pandas as pd


class Publication(BaseModel, allow_population_by_field_name=True):
    date: datetime.datetime = Field(alias="providerPublishTime")
    title: str
    publisher: str
    type: str
    url: str = Field(alias="link")


class News(BaseDataFrameModel):
    __root__: tp.List[Publication]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self._convert_to_df(index_column="date", sort_index=True)
        return self._df
