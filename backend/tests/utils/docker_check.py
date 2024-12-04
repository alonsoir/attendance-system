import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def check_docker() -> bool:
    """
    Verifica si Docker está disponible y corriendo.

    Returns:
        bool: True si Docker está disponible y corriendo, False en caso contrario
    """
    try:
        # Intenta ejecutar 'docker info'
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=True,
            text=True
        )
        logger.debug("Docker está corriendo correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar Docker: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("Docker no está instalado o no está en el PATH")
        return False


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