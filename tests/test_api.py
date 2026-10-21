import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["API_KEY"] = "secreta"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

H = {"X-API-Key": "secreta"}
PRODUCTO = {"sku": "LAP-001", "nombre": "Laptop", "categoria": "electronica", "precio": 15999.9, "stock": 4}


def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_health():
    with TestClient(app) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["base_de_datos"] == "conectada"


def test_requiere_api_key():
    with TestClient(app) as c:
        assert c.get("/api/v1/productos").status_code == 401


def test_flujo_completo():
    with TestClient(app) as c:
        r = c.post("/api/v1/productos", json=PRODUCTO, headers=H)
        assert r.status_code == 201
        pid = r.json()["id"]
        assert r.json()["stock_bajo"] is True  # 4 <= 5

        assert c.post("/api/v1/productos", json=PRODUCTO, headers=H).status_code == 409

        r = c.post(f"/api/v1/productos/{pid}/movimientos", json={"tipo": "entrada", "cantidad": 10}, headers=H)
        assert r.json()["stock"] == 14 and r.json()["stock_bajo"] is False

        r = c.post(f"/api/v1/productos/{pid}/movimientos", json={"tipo": "salida", "cantidad": 99}, headers=H)
        assert r.status_code == 422

        r = c.patch(f"/api/v1/productos/{pid}", json={"precio": 14999}, headers=H)
        assert float(r.json()["precio"]) == 14999

        r = c.get("/api/v1/productos?q=lap", headers=H)
        assert r.json()["total"] == 1

        r = c.get("/api/v1/productos/resumen", headers=H)
        assert r.json()["unidades_en_stock"] == 14

        assert c.delete(f"/api/v1/productos/{pid}", headers=H).status_code == 204
        assert c.get(f"/api/v1/productos/{pid}", headers=H).status_code == 404
