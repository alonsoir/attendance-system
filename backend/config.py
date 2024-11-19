import logging
import os
from pathlib import Path
from typing import List
from typing import Union, Optional

from dotenv import load_dotenv
from pydantic import ValidationInfo, field_validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # General settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Attendance System"
    VERSION: str = "0.1.0"
    BACKEND_PORT: str = "8000"
    FRONTEND_PORT: str = "3000"
    VITE_API_URL: str = "http://localhost:8000/api/v1"

    # Environment
    APP_ENV: str = "prod"
    DEBUG: bool = False
    PROJECT_ROOT: Path = Path(__file__).parent.parent

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:8000"])

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: Optional[str] = None

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        print("assemble_db_connection!")
        # Comprobamos si las variables de entorno están presentes antes de usarlas
        postgres_user = info.data.get("POSTGRES_USER")
        postgres_password = info.data.get("POSTGRES_PASSWORD")
        postgres_server = info.data.get("POSTGRES_SERVER")
        postgres_port = info.data.get("POSTGRES_PORT")
        postgres_db = info.data.get("POSTGRES_DB")

        print(
            postgres_user,
            postgres_password,
            postgres_server,
            postgres_port,
            postgres_db,
        )

        if not all(
            [
                postgres_user,
                postgres_password,
                postgres_server,
                postgres_port,
                postgres_db,
            ]
        ):
            raise ValueError(
                "CHECK!!! Algunas variables de configuración de PostgreSQL no están definidas"
            )

        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: Optional[str] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        if v:
            return v
        return f"redis://{info.data['REDIS_HOST']}:{info.data['REDIS_PORT']}/0"

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # External Services
    ANTHROPIC_API_KEY: str
    META_API_KEY: Optional[str]
    WHATSAPP_CALLBACK_TOKEN: Optional[str]
    WHATSAPP_PROVIDER: str = "mock"
    ENABLE_WHATSAPP: bool = False
    MOCK_EXTERNAL_SERVICES: bool = True

    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int
    GRAFANA_PORT: int
    GRAFANA_ADMIN_PASSWORD: str

    class Config:
        case_sensitive = True
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        # Determina el archivo .env según APP_ENV
        if "APP_ENV" in kwargs:
            env = kwargs["APP_ENV"]
        else:
            env = "dev"

        # Carga el archivo .env correspondiente
        env_file = f".env-{env}"
        load_dotenv(
            dotenv_path=env_file, verbose=True
        )  # Carga el archivo .env correspondiente
        # Verificación de que las variables de entorno están disponibles
        print(f"Loaded environment file: {env_file}")
        print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
        print(f"POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD')}")

        # Configura la variable env_file en Pydantic
        self.Config.env_file = env_file
        print(f"trying to load env_file {env_file}")
        super().__init__(**kwargs)
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Configuración cargada desde: {self.Config.env_file}")
