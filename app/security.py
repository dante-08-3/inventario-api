from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verificar_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Si API_KEY está configurada, exige el header X-API-Key en las rutas protegidas."""
    esperada = get_settings().api_key
    if esperada and api_key != esperada:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida o ausente (header X-API-Key)",
        )
