import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["INVENTORY_DB_PATH"] = str(Path("/tmp") / "manusmriti-inventory-test.sqlite")

from inventory_api.app import app


@pytest.fixture(autouse=True)
def _fresh_db() -> None:
    path = Path(os.environ["INVENTORY_DB_PATH"])
    path.unlink(missing_ok=True)


def _payload(**overrides):
    body = {
        "product_name": "USB-C Hub",
        "sku": "HUB-001",
        "price": 1499.0,
        "stock_quantity": 20,
        "category": "electronics",
    }
    body.update(overrides)
    return body


def test_health() -> None:
    assert TestClient(app).get("/health").status_code == 200


def test_create_and_get() -> None:
    client = TestClient(app)
    created = client.post("/products", json=_payload())
    assert created.status_code == 201
    product_id = created.json()["id"]
    assert created.json()["sku"] == "HUB-001"
    fetched = client.get(f"/products/{product_id}")
    assert fetched.status_code == 200
    assert fetched.json()["sku"] == "HUB-001"


def test_sku_is_normalized() -> None:
    client = TestClient(app)
    created = client.post("/products", json=_payload(sku="  hub-001  "))
    assert created.status_code == 201
    assert created.json()["sku"] == "HUB-001"


def test_duplicate_sku() -> None:
    client = TestClient(app)
    assert client.post("/products", json=_payload()).status_code == 201
    again = client.post("/products", json=_payload(product_name="Other"))
    assert again.status_code == 409
    assert "SKU" in again.json()["detail"]


def test_negative_price() -> None:
    client = TestClient(app)
    response = client.post("/products", json=_payload(price=-10))
    assert response.status_code == 422


def test_not_found() -> None:
    client = TestClient(app)
    assert client.get("/products/999").status_code == 404


def test_update_and_delete() -> None:
    client = TestClient(app)
    created = client.post("/products", json=_payload()).json()
    product_id = created["id"]
    updated = client.put(f"/products/{product_id}", json=_payload(product_name="USB-C Hub Pro", stock_quantity=5))
    assert updated.status_code == 200
    assert updated.json()["product_name"] == "USB-C Hub Pro"
    deleted = client.delete(f"/products/{product_id}")
    assert deleted.status_code == 204
    assert client.get(f"/products/{product_id}").status_code == 404
    assert client.delete(f"/products/{product_id}").status_code == 404


def test_pagination() -> None:
    client = TestClient(app)
    for index in range(12):
        client.post("/products", json=_payload(sku=f"SKU-{index:03d}", product_name=f"Item {index}"))
    page = client.get("/products", params={"page": 2, "page_size": 10})
    assert page.status_code == 200
    body = page.json()
    assert body["total"] == 12
    assert len(body["items"]) == 2
    assert body["page"] == 2
