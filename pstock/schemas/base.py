import typing as tp

import pandas as pd
from pydantic import BaseModel, Extra, PrivateAttr

_RootItemType = tp.Union[tp.Dict[str, tp.Any], BaseModel]


class BaseDataFrameModel(BaseModel):
    __root__: tp.Sequence[_RootItemType]
    _df: tp.Optional[pd.DataFrame] = PrivateAttr(default=None)

    def __iter__(self) -> tp.Iterator[_RootItemType]:  # type: ignore
        return iter(self.__root__)

    def __getitem__(self, item) -> _RootItemType:
        return self.__root__[item]

    def __len__(self) -> int:
        return len(self.__root__)

    def dict(self) -> tp.Sequence[_RootItemType]:  # type: ignore
        return super().dict()["__root__"]

    @property
    def df(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df
        self._df = pd.DataFrame(self.dict())
        return self._df

    class Config:
        extra = Extra.forbid
        allow_mutation = False
