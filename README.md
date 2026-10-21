# Inventario API

API REST de inventario hecha con **FastAPI + PostgreSQL**, empaquetada en **Docker**, desplegada en **Render** y consumida desde **n8n**.

- Documentación interactiva (Swagger): `/docs` · ReDoc: `/redoc`
- Salud del servicio: `/health`
- Autenticación por header `X-API-Key` (opcional en local)

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Estado de la API y de la base |
| GET | `/api/v1/productos` | Lista con búsqueda (`q`), filtro (`categoria`, `solo_stock_bajo`) y paginación |
| GET | `/api/v1/productos/resumen` | Totales, valor del inventario, productos con stock bajo |
| GET | `/api/v1/productos/{id}` | Un producto |
| POST | `/api/v1/productos` | Crear |
| PATCH | `/api/v1/productos/{id}` | Actualizar parcialmente |
| POST | `/api/v1/productos/{id}/movimientos` | Entrada / salida de stock |
| DELETE | `/api/v1/productos/{id}` | Eliminar |

## 1. Correr local con Docker (Postgres + API, imagen y volumen)

Necesitas Docker Desktop.

```bash
cp .env.example .env
docker compose up -d --build      # crea la imagen inventario-api:1.0.0 y el volumen inventario_pgdata
python scripts/seed.py            # carga productos de ejemplo
```

Abre http://localhost:8000/docs

Comandos útiles:

```bash
docker images | grep inventario   # ver la imagen
docker volume ls                  # ver el volumen inventario_pgdata
docker compose logs -f api        # ver logs
docker compose down               # apagar (los datos se quedan en el volumen)
docker compose down -v            # apagar y BORRAR los datos
```

### Solo Postgres en Docker, API con Python

```bash
docker compose up -d db
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## 2. Pruebas

```bash
pytest -q
```

## 3. Subir a GitHub

```bash
git remote add origin https://github.com/<tu-usuario>/inventario-api.git
git push -u origin main
```

## 4. Desplegar en Render

Opción A (Blueprint): en Render → **New → Blueprint** → elige el repo. `render.yaml` crea la base y la API.
Opción B: crea un **Web Service** con runtime Docker y define `DATABASE_URL`, `API_KEY`, `ENVIRONMENT`.

Cada `git push` a `main` vuelve a desplegar.

## 5. Consumir desde n8n (n8n en Docker)

`docker compose up -d` también levanta n8n en http://localhost:5678 (volumen `inventario_n8ndata`).
El flujo lee la URL y la llave de `INVENTARIO_URL` e `INVENTARIO_API_KEY` en tu `.env`.

1. Abre http://localhost:5678 y crea tu cuenta de n8n (solo la primera vez).
2. Importa el flujo:
   ```bash
   docker compose exec n8n n8n import:workflow --input=/workflows/workflow-inventario.json
   ```
3. Recarga n8n, abre "Inventario API - alerta de stock bajo" y dale **Execute workflow**.
4. Conecta el nodo final a Telegram, Gmail, Slack, etc. para recibir alertas de stock bajo.

> Nota: en el plan gratis de Render el servicio se duerme tras ~15 min sin tráfico; la primera petición tarda unos segundos en despertarlo.
