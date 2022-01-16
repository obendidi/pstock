import typing as tp

import pandas as pd
import pytest
from pydantic import BaseModel, ValidationError

from pstock.schemas.base import BaseDataFrameModel


class _TestModel(BaseModel):
    x: int
    y: int
    z: int


class _TestSequenceDFModel(BaseDataFrameModel):
    __root__: tp.List[_TestModel]


class _TestMappingDFModelSimple(BaseDataFrameModel):
    __root__: tp.Dict[str, _TestModel]  # type: ignore


class _TestMappingDFModelComplex(BaseDataFrameModel):
    __root__: tp.Dict[str, _TestSequenceDFModel]


def test_base_dataframe_model_parse_obj_with_list_of_dicts():
    data = [
        {"x": 1, "y": 1, "z": 1},
        {"x": 2, "y": 2, "z": 2},
        {"x": 3, "y": 3, "z": 3},
    ]
    with pytest.raises(ValidationError):
        BaseDataFrameModel.parse_obj(data)


def test_base_dataframe_model_parse_obj_with_dict_of_list_of_dicts():
    data = {
        "key1": [
            {"x": 1, "y": 1, "z": 1},
            {"x": 2, "y": 2, "z": 2},
            {"x": 3, "y": 3, "z": 3},
        ],
        "key2": [
            {"x": 4, "y": 4, "z": 4},
            {"x": 5, "y": 5, "z": 5},
            {"x": 6, "y": 6, "z": 6},
        ],
    }
    with pytest.raises(ValidationError):
        BaseDataFrameModel.parse_obj(data)


def test_base_dataframe_model_parse_obj_with_test_sequence_df_model():
    data = [
        {"x": 1, "y": 1, "z": 1},
        {"x": 2, "y": 2, "z": 2},
        {"x": 3, "y": 3, "z": 3},
    ]
    df_model = _TestSequenceDFModel.parse_obj(data)
    assert isinstance(df_model, BaseModel)
    assert isinstance(df_model, tp.Iterable)
    assert len(df_model) == 3
    assert df_model[0] == _TestModel(x=1, y=1, z=1)
    assert df_model[1] == _TestModel(x=2, y=2, z=2)
    assert df_model[2] == _TestModel(x=3, y=3, z=3)

    with pytest.raises(IndexError):
        df_model[3]
    assert data == [model.dict() for model in df_model]
    assert df_model._df is None
    assert isinstance(df_model.df, pd.DataFrame)
    assert df_model._df is not None
    assert id(df_model._df) == id(df_model.df)
    assert df_model.df.equals(pd.DataFrame(data))


def test_base_dataframe_model_parse_obj_with_test_sequence_df_model_invalid():

    data = [{"a": 1}]
    with pytest.raises(ValidationError):
        _TestSequenceDFModel.parse_obj(data)


def test_base_dataframe_model_parse_obj_with_test_mapping_df_model_simple():
    data = {
        "key1": {"x": 1, "y": 1, "z": 1},
        "key2": {"x": 2, "y": 2, "z": 2},
    }
    with pytest.raises(ValidationError):
        _TestMappingDFModelSimple.parse_obj(data)


def test_base_dataframe_model_parse_obj_with_test_mapping_df_model_complex():
    data = {
        "key1": [
            {"x": 1, "y": 1, "z": 1},
            {"x": 2, "y": 2, "z": 2},
            {"x": 3, "y": 3, "z": 3},
        ],
        "key2": [
            {"x": 4, "y": 4, "z": 4},
            {"x": 5, "y": 5, "z": 5},
            {"x": 6, "y": 6, "z": 6},
        ],
    }

    df_model = _TestMappingDFModelComplex.parse_obj(data)
    assert isinstance(df_model, BaseModel)
    assert isinstance(df_model, tp.Iterable)
    assert len(df_model) == 2
    for key in df_model:
        assert isinstance(df_model[key], _TestSequenceDFModel)
        for submodel in df_model[key]:
            assert isinstance(submodel, _TestModel)
    assert df_model._df is None
    assert isinstance(df_model.df, pd.DataFrame)
    assert df_model.df["key1"].equals(_TestSequenceDFModel.parse_obj(data["key1"]).df)
    assert df_model.df["key2"].equals(_TestSequenceDFModel.parse_obj(data["key2"]).df)
