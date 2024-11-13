"""
Test suite for the Attendance System.
"""

import os

import pytest

# Asegurar que estamos en modo de prueba
os.environ["TESTING"] = "1"

# Configurar el registro para las pruebas
import logging

logging.basicConfig(level=logging.DEBUG)
