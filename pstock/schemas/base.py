import typing as tp
from collections.abc import Sequence

import pandas as pd
from pydantic import BaseModel, Extra, PrivateAttr, ValidationError, validator
from pydantic.fields import ModelField


class BaseDataFrameModel(BaseModel):
    """A custom `pydantic.BaseModel` with support for convertion to a `pandas.DataFrame`

    Examples:

    * With a list of pydantic.BaseModels:

    ```py
    import typing

    from pydantic import BaseModel
    from pstock.schemas import BaseDataFrameModel

    class MyModel(BaseModel):
        x: int
        y: int

    class MyDfModel(BaseDataFrameModel):
        __root__: typing.List[MyModel]

    model = MyDfModel.parse_obj([{"x": 0, "y": 0}, {"x": 1, "y": 1}])
    print(model) # MyDfModel(__root__=[MyModel(x=0, y=0), MyModel(x=1, y=1)])

    print(model.df)
    #    x  y
    # 0  0  0
    # 1  1  1
    ```

    * With a mapping of [BaseDataFrameModels][pstock.schemas.BaseDataFrameModel]:

    ```py
    import typing

    from pydantic import BaseModel
    from pstock.schemas import BaseDataFrameModel

    class MyModel(BaseModel):
        x: int
        y: int

    class MyDfModel(BaseDataFrameModel):
        __root__: typing.List[MyModel]

    class MyMappingDfModel(BaseDataFrameModel):
        __root__: typing.Dict[str, MyDfModel]

    model = MyMappingDfModel.parse_obj({"key1": [{"x": 0, "y": 0}, {"x": 1, "y": 1}],
                                        "key2": [{"x": 2, "y": 2}, {"x": 3, "y": 3}]})
    print(model) # MyMappingDfModel(__root__={'key1': MyDfModel(__root__=[MyModel(x=0, y=0), MyModel(x=1, y=1)]), 'key2': MyDfModel(__root__=[MyModel(x=2, y=2), MyModel(x=3, y=3)])}) # noqa

    print(model.df)
    #   key1    key2
    #      x  y    x  y
    # 0    0  0    2  2
    # 1    1  1    3  3
    ```

    """

    __root__: tp.Union[tp.Sequence[BaseModel], tp.Mapping[str, "BaseDataFrameModel"]]
    _df: tp.Optional[pd.DataFrame] = PrivateAttr(default=None)

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item) -> BaseModel:
        return self.__root__[item]

    def __len__(self) -> int:
        return len(self.__root__)

    def _convert_to_df(
        self, index_column: tp.Optional[str] = None, sort_index: bool = False
    ) -> pd.DataFrame:
        if isinstance(self.__root__, Sequence):
            df = pd.DataFrame.from_dict(self.dict().get("__root__"), orient="columns")
        else:
            df = pd.concat(
                [model.df for model in self.__root__.values()],
                axis=1,
                keys=self.__root__.keys(),
            )
        if index_column is not None and not df.empty:
            df = df.set_index(index_column)
            if sort_index:
                df = df.sort_index()
        return df

    @property
    def df(self) -> pd.DataFrame:
        """Convert __root__ field into a pandas.DataFrame.

        The DataFrame is cached in a private attribute `._df` that is used in
        subsequent calls.

        Returns:
            pd.DataFrame:
        """
        if self._df is None:
            self._df = self._convert_to_df()
        return self._df

    @validator("__root__")
    def _validate_root(cls, root_values):
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


ComputedType = tp.TypeVar("ComputedType")


class Computed(tp.Generic[ComputedType]):
    validate_always = True

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls,
        func: tp.Callable,
        field: ModelField,
        values: tp.Dict[str, tp.Any],
    ):
        if not field.sub_fields:
            raise TypeError(
                "No subField provided for Generic type 'Computed' in field "
                f"'{field.name}', example: 'Computed[int]'"
            )
        try:
            result = func(**values)
        except Exception as func_error:
            raise ValueError(
                f"Error calling function {func} for field '{field.name}': {func_error}"
            )
        typ = field.sub_fields[0]
        validated, error = typ.validate(result, {}, loc="Computed")
        if error:
            raise ValidationError([error], cls)  # type: ignore
        return validated
