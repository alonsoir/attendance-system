import logging
import subprocess
from typing import Optional

from docker.errors import DockerException

logger = logging.getLogger(__name__)

import docker


def check_docker() -> bool:
    """Verifica que Docker está disponible y corriendo."""
    try:
        client=docker.from_env()
        print("---> imprimiendo docker info")
        print(client.info())
        client.ping()  # Esto lanzará una excepción si no puede conectar
        version = client.version()
        logger.info(f"Docker conectado correctamente. Versión: {version.get('Version', 'unknown')}")
        for container in client.containers.list():
            logger.info(f"Contenedor en ejecución: {container.name} - {container.status}")
        return True
    except docker.errors.APIError as e:
        logger.error(f"Error conectando con Docker: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al verificar Docker: {str(e)}")
        return False

def check_containers(client):
    """Verifica que los contenedores esperados están en ejecución."""
    try:
        for container in client.containers.list():
            logger.info(f"Contenedor en ejecución: {container.name} - {container.status}")
    except docker.errors.APIError as e:
        logger.error(f"Error al listar contenedores: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado al verificar contenedores: {str(e)}")


def get_docker_version() -> Optional[str]:
    """
    Obtiene la versión de Docker instalada.

    Returns:
        Optional[str]: Versión de Docker o None si no se puede obtener
    """
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            check=True,
            text=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None