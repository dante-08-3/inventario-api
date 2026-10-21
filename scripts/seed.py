"""Carga productos de ejemplo. Uso: python scripts/seed.py [URL] [API_KEY]"""
import json
import sys
import urllib.request

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
KEY = sys.argv[2] if len(sys.argv) > 2 else ""

PRODUCTOS = [
    {"sku": "LAP-001", "nombre": "Laptop 14\"", "categoria": "electronica", "precio": 15999.90, "stock": 12},
    {"sku": "MOU-002", "nombre": "Mouse inalámbrico", "categoria": "accesorios", "precio": 349.00, "stock": 3},
    {"sku": "TEC-003", "nombre": "Teclado mecánico", "categoria": "accesorios", "precio": 1299.00, "stock": 25},
    {"sku": "MON-004", "nombre": "Monitor 27\" 4K", "categoria": "electronica", "precio": 7499.00, "stock": 2},
    {"sku": "CAB-005", "nombre": "Cable USB-C 2 m", "categoria": "accesorios", "precio": 189.00, "stock": 80},
]

for p in PRODUCTOS:
    req = urllib.request.Request(
        f"{URL}/api/v1/productos",
        data=json.dumps(p).encode(),
        headers={"Content-Type": "application/json", "X-API-Key": KEY},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            print("OK ", p["sku"], r.status)
    except urllib.error.HTTPError as e:
        print("-- ", p["sku"], e.code, e.read().decode())
