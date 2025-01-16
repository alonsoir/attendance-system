import logging
import os
import subprocess
from typing import Optional

from docker.errors import DockerException

logger = logging.getLogger(__name__)

import docker

def check_docker() -> bool:
    """Verifies that Docker is available and running."""
    try:
        # Manually set the Unix socket URL. This is necessary for my MBP, but will fail on other systems.
        docker_host = "unix:///Users/aironman/.docker/run/docker.sock"
        # wrong way
        # client = docker.DockerClient(base_url=docker_host)
        # correct way
        client = docker.from_env()

        print("---> Printing Docker info")
        print(client.info())
        client.ping()  # This will raise an exception if it can't connect
        version = client.version()
        print(f"Docker connected successfully. Version: {version.get('Version', 'unknown')}")
        for container in client.containers.list():
            print(f"Running container: {container.name} - {container.status}")
        return True
    except docker.errors.APIError as e:
        print(f"Error connecting to Docker: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error when verifying Docker: {str(e)}")
        return False

def check_containers(client):
    """Verifica que los contenedores esperados están en ejecución."""
    try:
        for container in client.containers.list():
            logger.info(
                f"Contenedor en ejecución: {container.name} - {container.status}"
            )
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
            ["docker", "--version"], capture_output=True, check=True, text=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
