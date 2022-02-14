from __future__ import annotations

import typing as tp
from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd
import pendulum
from pydantic import BaseModel as _BaseModel
from pydantic import PrivateAttr


class BaseModel(_BaseModel):
    _created_at: datetime = PrivateAttr(default_factory=pendulum.now)

    @property
    def created_at(self) -> datetime:
        return self._created_at


class BaseModelDf(BaseModel, ABC):

    _df: tp.Optional[pd.DataFrame] = PrivateAttr(default=None)

    @abstractmethod
    def gen_df(self) -> pd.DataFrame:
        ...

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self.gen_df()
        return self._df


T = tp.TypeVar("T", bound=BaseModel)


class BaseModelSequence(tp.Generic[T], BaseModelDf):

    __root__: tp.Sequence[T]

    @tp.overload
    def __getitem__(self, index: int) -> T:
        """Get single item from __root__ by idx."""

    @tp.overload
    def __getitem__(self, index: slice) -> tp.Sequence[T]:
        """Get slice of items from __root__ by idx."""

    def __getitem__(self, index):
        return self.__root__[index]

    def __len__(self) -> int:
        return len(self.__root__)

    def __iter__(self) -> tp.Iterator[T]:  # type: ignore
        return iter(self.__root__)

    def gen_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.dict().get("__root__"), orient="columns")


U = tp.TypeVar("U", bound=BaseModelSequence)


class BaseModelMapping(tp.Generic[U], BaseModelDf):

    __root__: tp.Mapping[str, U]

    def __getitem__(self, index: str) -> U:
        return self.__root__[index]

    def __len__(self) -> int:
        return len(self.__root__)

    def __iter__(self) -> tp.Iterator[str]:  # type: ignore
        return iter(self.__root__)

    def gen_df(self) -> pd.DataFrame:
        keys, dfs = zip(*[(key, value.df) for key, value in self.__root__.items()])
        return pd.concat(dfs, axis=1, keys=keys)
