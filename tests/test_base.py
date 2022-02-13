import typing as tp

import pandas as pd
import pendulum

from pstock.base import BaseModel, BaseModelDf, BaseModelMapping, BaseModelSequence


def test_pstock_base_model(pendulum_now: pendulum.DateTime):
    model = BaseModel()
    assert model.created_at == pendulum_now


def test_pstock_base_model_df(pendulum_now: pendulum.DateTime):
    class TestModel(BaseModelDf):
        def _gen_df(self) -> pd.DataFrame:
            return pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})

    model = TestModel()
    assert model.created_at == pendulum_now
    assert model._df is None
    assert model.df is not None
    assert model._df is not None
    assert model.df.equals(pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]}))


def test_pstock_base_model_sequence(pendulum_now: pendulum.DateTime):
    class TestModel(BaseModel):
        col1: int
        col2: int

    class TestModelSequence(BaseModelSequence[TestModel]):
        __root__: tp.List[TestModel]

    model = TestModelSequence.parse_obj(
        [{"col1": 1, "col2": 3}, {"col1": 2, "col2": 4}]
    )

    assert model.created_at == pendulum_now
    assert len(model) == 2
    assert len(model[:1]) == 1
    assert all(isinstance(sub, TestModel) for sub in model)
    assert model[0] == TestModel(col1=1, col2=3)
    assert model[1] == TestModel(col1=2, col2=4)
    assert model[:1] == [TestModel(col1=1, col2=3)]
    assert model.df.equals(pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]}))


def test_pstock_base_model_mapping(pendulum_now: pendulum.DateTime):
    class TestModel(BaseModel):
        col1: int
        col2: int

    class TestModelSequence(BaseModelSequence[TestModel]):
        __root__: tp.List[TestModel]

    class TestModelMapping(BaseModelMapping[TestModelSequence]):
        __root__: tp.Dict[str, TestModelSequence]

    model = TestModelMapping.parse_obj(
        {
            "key1": [{"col1": 1, "col2": 3}, {"col1": 2, "col2": 4}],
            "key2": [{"col1": 5, "col2": 7}, {"col1": 6, "col2": 8}],
        }
    )
    submodel1 = TestModelSequence.parse_obj(
        [{"col1": 1, "col2": 3}, {"col1": 2, "col2": 4}]
    )
    submodel2 = TestModelSequence.parse_obj(
        [{"col1": 5, "col2": 7}, {"col1": 6, "col2": 8}]
    )

    assert model.created_at == pendulum_now
    assert len(model) == 2
    assert [key for key in model] == ["key1", "key2"]
    assert model["key1"] == submodel1
    assert model["key2"] == submodel2
    assert isinstance(model.df, pd.DataFrame)
    assert model.df["key1"].equals(submodel1.df)
    assert model.df["key2"].equals(submodel2.df)
