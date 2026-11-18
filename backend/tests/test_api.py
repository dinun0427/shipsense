VALID = {
    "purchase_timestamp": "2018-05-10T10:00:00",
    "approved_timestamp": "2018-05-10T10:30:00",
    "estimated_delivery_date": "2018-05-25T00:00:00",
    "customer_state": "SP",
    "seller_state": "RJ",
    "price_sum": 120.0,
    "freight_sum": 25.0,
    "distance_km": 430.0,
}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_predict_returns_probability(client):
    r = client.post("/api/v1/predict-delay", json=VALID)
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["late_probability"] <= 1
    assert body["risk_label"] in {"low", "medium", "high"}


def test_predict_rejects_negative_price(client):
    r = client.post("/api/v1/predict-delay", json={**VALID, "price_sum": -5})
    assert r.status_code == 422


def test_predict_rejects_bad_state(client):
    r = client.post("/api/v1/predict-delay", json={**VALID, "customer_state": "SAO"})
    assert r.status_code == 422


def test_prediction_is_stored(client):
    client.post("/api/v1/predict-delay", json=VALID)
    rows = client.get("/api/v1/predictions").json()
    assert len(rows) == 1
    assert rows[0]["model_version"] == "test"


def test_review_empty_text_rejected(client):
    assert client.post("/api/v1/analyze-review", json={"text": ""}).status_code == 422


def test_review_ok(client):
    r = client.post("/api/v1/analyze-review", json={"text": "produto chegou atrasado"})
    assert r.json()["sentiment"] == "negative"
