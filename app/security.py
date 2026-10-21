from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verificar_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """Si API_KEY está configurada, exige el header X-API-Key en las rutas protegidas."""
    settings = get_settings()
    esperada = settings.api_key
    if not esperada:
        # En local se permite sin llave; en producción nunca quedar abierta por error.
        if settings.environment in ("local", "docker"):
            return
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEY no configurada en el servidor",
        )
    if api_key != esperada:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida o ausente (header X-API-Key)",
        )
