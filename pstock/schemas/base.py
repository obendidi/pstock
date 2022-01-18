import typing as tp
from collections.abc import Sequence

import pandas as pd
from pydantic import BaseModel, Extra, PrivateAttr, validator


class BaseDataFrameModel(BaseModel):

    __root__: tp.Union[tp.Sequence[BaseModel], tp.Mapping[str, "BaseDataFrameModel"]]
    _df: tp.Optional[pd.DataFrame] = PrivateAttr(default=None)

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item) -> BaseModel:
        return self.__root__[item]

    def __len__(self) -> int:
        return len(self.__root__)

    def dict(  # type: ignore
        self,
    ) -> tp.Union[
        tp.Sequence[tp.Dict[str, tp.Any]], tp.Mapping[str, tp.Dict[str, tp.Any]]
    ]:
        return super().dict()["__root__"]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df

        if isinstance(self.__root__, Sequence):
            self._df = pd.DataFrame.from_dict(self.dict(), orient="columns")
        else:  # only mapping is supported if not a sequence
            dfs = {key: value.df for key, value in self.__root__.items()}
            self._df = pd.concat(dfs.values(), axis=1, keys=dfs.keys())
        return self._df

    @validator("__root__")
    def validate_root(cls, root_values):
        if isinstance(root_values, Sequence):
            if any(type(root_value) is BaseModel for root_value in root_values):
                raise ValueError(
                    "'BaseDataFrameModel' should not be used as is. Its is meant to be "
                    "subclassed and defining a custom root type with a custom pydantic "
                    "BaseModel."
                )
        else:
            if not all(isinstance(v, BaseDataFrameModel) for v in root_values.values()):
                raise ValueError(
                    "When using 'BaseDataFrameModel' with a mapping as __root__, "
                    "mapping values should all be instances of 'BaseDataFrameModel'."
                )
        return root_values

    class Config:
        extra = Extra.forbid
        allow_mutation = False
