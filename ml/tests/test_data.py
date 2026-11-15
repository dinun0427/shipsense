from pathlib import Path

import pandas as pd
import pytest

from shipsense_ml.data.make_dataset import haversine_km

ROOT = Path(__file__).resolve().parents[2]
ORDERS = ROOT / "data" / "processed" / "orders_features.parquet"
needs_data = pytest.mark.skipif(
    not ORDERS.exists(), reason="processed data not built yet"
)


def test_haversine_known_distance():
    # Sao Paulo to Rio de Janeiro is roughly 360 km in a straight line.
    d = haversine_km(-23.55, -46.63, -22.91, -43.17)
    assert d == pytest.approx(360, abs=15)


def test_haversine_zero_distance():
    assert haversine_km(-23.55, -46.63, -23.55, -46.63) == pytest.approx(0, abs=1e-6)


@needs_data
def test_no_duplicate_orders():
    df = pd.read_parquet(ORDERS)
    assert df.order_id.is_unique


@needs_data
def test_target_is_binary():
    df = pd.read_parquet(ORDERS)
    assert set(df.is_late.unique()) <= {0, 1}


@needs_data
def test_late_rate_is_sane():
    df = pd.read_parquet(ORDERS)
    assert 0.03 < df.is_late.mean() < 0.20


@needs_data
def test_dates_make_sense():
    df = pd.read_parquet(ORDERS)
    assert (df.promised_days > 0).all()
    assert (df.approval_hours >= 0).all()
