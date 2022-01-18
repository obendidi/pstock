import pendulum
import pytest
from pydantic import ValidationError

from pstock.yahoo_finance.utils import _YFChartParams


def test_yf_chart_params_aliases():
    params = _YFChartParams(
        interval="1m",
        period="1d",
        start=1346887571,
        end=1346889571,
        includePrePost=True,
        events="div",
    )

    assert params.dict(exclude_none=True, by_alias=True) == {
        "interval": "1m",
        "range": "1d",
        "period1": 1346887571,
        "period2": 1346889571,
        "includePrePost": True,
        "events": "div",
    }


def test_yf_chart_params_end_value_factory_with_no_start():
    params = _YFChartParams(
        interval="1m",
        period="1d",
    )
    assert params.dict(exclude_none=True, by_alias=True) == {
        "interval": "1m",
        "range": "1d",
        "includePrePost": False,
        "events": "div,splits",
    }


def test_yf_chart_params_with_no_start_and_no_period():
    params = _YFChartParams(
        interval="1m",
        period="1d",
    )
    with pytest.raises(ValidationError):
        params.interval = "mm"


def test_yf_chart_params_setting_invalid_interval():
    with pytest.raises(ValidationError):
        _YFChartParams(interval="1m")


def test_yf_chart_params_end_value_factory_with_start():
    known = pendulum.datetime(2021, 5, 21, 12)
    pendulum.set_test_now(known)
    params = _YFChartParams(
        interval="1m",
        start=1346887571,
    )
    assert params.dict(exclude_none=True, by_alias=True) == {
        "interval": "1m",
        "period1": 1346887571,
        "period2": 1621598400,
        "includePrePost": False,
        "events": "div,splits",
    }
    pendulum.set_test_now()
