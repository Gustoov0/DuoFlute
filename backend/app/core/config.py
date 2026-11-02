from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Lê as configurações das variáveis de ambiente (definidas no docker-compose/.env).

    O nome do campo corresponde à variável: database_url <- DATABASE_URL.
    Campos sem valor padrão são OBRIGATÓRIOS: se faltarem, a aplicação nem inicia.
    """

    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 60
    redis_url: str = ""


settings = Settings()