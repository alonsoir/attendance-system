"""
Test suite for the Attendance System.
"""

import pytest
import os

# Asegurar que estamos en modo de prueba
os.environ["TESTING"] = "1"

# Configurar el registro para las pruebas
import logging

logging.basicConfig(level=logging.DEBUG)
