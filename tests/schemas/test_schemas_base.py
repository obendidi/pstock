import typing as tp

import pandas as pd
import pytest
from pydantic import BaseModel, ValidationError

from pstock.schemas.base import BaseDataFrameModel


class _TestModel(BaseModel):
    x: int
    y: int


@pytest.mark.parametrize(
    "data",
    [
        [{"x": 1, "y": -1}, {"x": 2, "y": -2}, {"x": 3, "y": -3}],
        [_TestModel(x=1, y=-1), _TestModel(x=2, y=-2)],
    ],
    ids=["dict-items", "pydantic-model-items"],
)
def test_base_dataframe_model_with_simple_dicts(data):

    models = BaseDataFrameModel.parse_obj(data)

    assert isinstance(models, BaseModel)
    assert isinstance(models, tp.Iterable)
    assert len(models) == len(data)
    assert models[0] == data[0]
    assert data == [model for model in models]
    assert models.dict() == data
    assert models._df is None
    assert isinstance(models.df, pd.DataFrame)
    assert models._df is not None
    assert len(models.df) == len(data)


class _TestDataFrameModel(BaseDataFrameModel):
    __root__: tp.List[_TestModel]


@pytest.mark.parametrize(
    "data",
    [
        [{"x": 1, "y": -1}, {"x": 2, "y": -2}, {"x": 3, "y": -3}],
        [_TestModel(x=1, y=-1), _TestModel(x=2, y=-2)],
    ],
    ids=["dict-items", "pydantic-model-items"],
)
def test_child_dataframe_model(data):
    models = _TestDataFrameModel.parse_obj(data)

    assert isinstance(models, BaseModel)
    assert isinstance(models, tp.Iterable)
    assert len(models) == len(data)
    assert all(isinstance(model, _TestModel) for model in models)
    assert models[0] == data[0]
    assert data == [model for model in models]
    assert models.dict() == data
    assert models._df is None
    assert isinstance(models.df, pd.DataFrame)
    assert models._df is not None
    assert len(models.df) == len(data)


def test_child_dataframe_model_invalid_data():

    data = [{"z": 1}]
    with pytest.raises(ValidationError):
        _TestDataFrameModel.parse_obj(data)
