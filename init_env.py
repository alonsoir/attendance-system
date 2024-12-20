import os


def create_env_file():
    env_file = ".env-development"
    default_content = """
# Archivo de configuración para el entorno de desarrollo
PROJECT_NAME="Attendance System (Dev)"
PROJECT_DESCRIPTION="Attendance System (Dev)"
VERSION=0.1.0
API_V1_STR=/api/v1
BACKEND_CORS_ORIGINS=http://localhost:8000
ENABLE_METRICS=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=admin
BACKEND_PORT=8000
ENABLE_WHATSAPP_CALLBACK=true
MOCK_EXTERNAL_SERVICES=true
POSTGRES_SERVER=localhost
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password
POSTGRES_DB=test_db
POSTGRES_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379
SECRET_KEY=supersecretkey
ANTHROPIC_API_KEY=supersecretkey
WHATSAPP_CALLBACK_TOKEN=supersecretkey
WHATSAPP_META_API_KEY=NOT_SET_YET
WHATSAPP_PROVIDER=callmebot
FRONTEND_PORT=3000
VITE_API_URL=http://localhost:3000

    """.strip()

    if not os.path.exists(env_file):
        with open(env_file, "w") as file:
            file.write(default_content)
        print(f"{env_file} creado con valores predeterminados.")
    else:
        print(f"{env_file} ya existe. No se realizaron cambios.")


if __name__ == "__main__":
    create_env_file()
