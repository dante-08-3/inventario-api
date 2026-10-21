from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración leída de variables de entorno (o del archivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Inventario API"
    app_version: str = "1.0.0"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://inventario:inventario@localhost:5432/inventario"
    api_key: str = ""  # si está vacía, la API no pide llave (útil en local)
    cors_origins: str = "*"

    @property
    def sqlalchemy_url(self) -> str:
        # Render entrega URLs "postgres://" o "postgresql://"; SQLAlchemy + psycopg3 necesita el driver explícito.
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://"):]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
