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
    {"sku": "AUD-006", "nombre": "Audífonos Bluetooth", "categoria": "audio", "precio": 899.00, "stock": 18},
    {"sku": "BOC-007", "nombre": "Bocina portátil", "categoria": "audio", "precio": 1149.00, "stock": 4},
    {"sku": "IMP-008", "nombre": "Impresora multifuncional", "categoria": "oficina", "precio": 3299.00, "stock": 6},
    {"sku": "TIN-009", "nombre": "Cartucho de tinta negra", "categoria": "oficina", "precio": 429.00, "stock": 40},
    {"sku": "SSD-010", "nombre": "Disco SSD 1 TB", "categoria": "almacenamiento", "precio": 1599.00, "stock": 15},
    {"sku": "USB-011", "nombre": "Memoria USB 64 GB", "categoria": "almacenamiento", "precio": 179.00, "stock": 1},
    {"sku": "CAM-012", "nombre": "Cámara web 1080p", "categoria": "accesorios", "precio": 749.00, "stock": 9},
    {"sku": "ROU-013", "nombre": "Router WiFi 6", "categoria": "redes", "precio": 1899.00, "stock": 7},
    {"sku": "SIL-014", "nombre": "Silla ergonómica", "categoria": "oficina", "precio": 4599.00, "stock": 3},
    {"sku": "TAB-015", "nombre": "Tablet 10\"", "categoria": "electronica", "precio": 5299.00, "stock": 11},
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
