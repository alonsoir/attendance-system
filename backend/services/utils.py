import re
from enum import Enum
from typing import Dict

from backend.services.service_status import check_service_status


class Language(str, Enum):
    EN_US = "en-US"
    ES_ES = "es-ES"


class Region(str, Enum):
    US = "US"
    ES = "ES"


# Service Status Constants
SERVICE_STATUS = {
    "ONLINE": "online",
    "OFFLINE": "offline",
    "DEGRADED": "degraded",
    "UNKNOWN": "unknown",
}

# Message Types
MESSAGE_TYPES = {
    "ABSENCE_NOTIFICATION": "absence_notification",
    "FOLLOW_UP": "follow_up",
    "STATUS_UPDATE": "status_update",
    "RESPONSE": "response",
    "ERROR": "error",
}

# Sensitivity Levels
SENSITIVITY_LEVELS = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

# Response Templates by Language
RESPONSE_TEMPLATES: Dict[str, Dict[str, str]] = {
    Language.EN_US: {
        "INITIAL_CONTACT": """
        Dear {student_name}'s guardian,

        We are reaching out from {school_name} regarding your student's absence. 
        Could you please provide information about the reason for the absence?

        Best regards,
        Attendance Department
        """,
        "FOLLOW_UP": """
        Dear {student_name}'s guardian,

        We are following up on the previously reported absence.
        {additional_message}

        Best regards,
        Attendance Department
        """,
        "EMERGENCY": """
        Dear {student_name}'s guardian,

        We need to contact you urgently regarding your student's absence.
        Please contact us as soon as possible at {contact_number}.

        Best regards,
        Attendance Department
        """,
        "MEDICAL": """
        Dear {student_name}'s guardian,

        We understand your student is absent due to medical reasons. 
        Please provide a doctor's note upon their return to school.

        Best regards,
        Attendance Department
        """,
    },
    Language.ES_ES: {
        "INITIAL_CONTACT": """
        Estimado/a tutor/a de {student_name}:

        Nos ponemos en contacto desde {school_name} en relación con la ausencia del alumno/a. 
        ¿Podría proporcionarnos información sobre el motivo de la ausencia?

        Atentamente,
        Departamento de Asistencia
        """,
        "FOLLOW_UP": """
        Estimado/a tutor/a de {student_name}:

        Realizamos un seguimiento sobre la ausencia notificada anteriormente.
        {additional_message}

        Atentamente,
        Departamento de Asistencia
        """,
        "EMERGENCY": """
        Estimado/a tutor/a de {student_name}:

        Necesitamos contactar con usted urgentemente en relación con la ausencia del alumno/a.
        Por favor, póngase en contacto con nosotros lo antes posible en el {contact_number}.

        Atentamente,
        Departamento de Asistencia
        """,
        "MEDICAL": """
        Estimado/a tutor/a de {student_name}:

        Entendemos que el alumno/a está ausente por motivos médicos. 
        Por favor, proporcione un justificante médico cuando se reincorpore al centro.

        Atentamente,
        Departamento de Asistencia
        """,
    },
}

# Error Messages by Language
ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    Language.EN_US: {
        "CLAUDE_API_ERROR": "Error contacting Claude service",
        "WHATSAPP_API_ERROR": "Error sending WhatsApp message",
        "DATABASE_ERROR": "Database error",
        "INVALID_PHONE": "Invalid phone number",
        "UNAUTHORIZED": "Unauthorized to perform this action",
        "STUDENT_NOT_FOUND": "Student not found in the system",
        "MISSING_DATA": "Incomplete or missing data",
    },
    Language.ES_ES: {
        "CLAUDE_API_ERROR": "Error al contactar con el servicio de Claude",
        "WHATSAPP_API_ERROR": "Error al enviar mensaje de WhatsApp",
        "DATABASE_ERROR": "Error en la base de datos",
        "INVALID_PHONE": "Número de teléfono inválido",
        "UNAUTHORIZED": "No autorizado para realizar esta acción",
        "STUDENT_NOT_FOUND": "Estudiante no encontrado en el sistema",
        "MISSING_DATA": "Datos incompletos o faltantes",
    },
}

# Phone Number Patterns by Region
PHONE_PATTERNS = {
    Region.US: {
        "pattern": r"^\+1[2-9]\d{9}$",
        "format": "+1XXXXXXXXXX",
        "example": "+12125551234",
        "description": "US phone number starting with +1 followed by area code and 7 digits",
    },
    Region.ES: {
        "pattern": r"^\+34[6789]\d{8}$",
        "format": "+34XXXXXXXXX",
        "example": "+34612345678",
        "description": "Spanish phone number starting with +34 followed by 9 digits",
    },
}

# Configuration Constants
CONFIG = {
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 5,  # seconds
    "MESSAGE_TIMEOUT": 30,  # seconds
    "MAX_MESSAGE_LENGTH": 1000,
    "MIN_SENSITIVITY_SCORE": 0,
    "MAX_SENSITIVITY_SCORE": 10,
    "DEFAULT_LANGUAGE": Language.ES_ES,
    "SUPPORTED_LANGUAGES": [Language.EN_US, Language.ES_ES],
    "DEFAULT_REGION": Region.ES,
    "LOG_LEVEL": "INFO",
    "CACHE_TTL": 3600,  # 1 hour
}

# Extended Validation Rules
VALIDATION_RULES = {
    "NAME_RULES": {
        "MIN_LENGTH": 2,
        "MAX_LENGTH": 50,
        "PATTERN": r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$",
    },
    "EMAIL_RULES": {
        "PATTERN": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "MAX_LENGTH": 255,
    },
}

import phonenumbers
from phonenumbers import NumberParseException

class PhoneNumberValidator:
    # Lista de países permitidos
    ALLOWED_REGIONS = {'ES', 'US'}

    # Prefijos válidos para números españoles
    VALID_ES_PREFIXES = {'6', '7', '8', '9'}

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Valida el número de teléfono para España y Estados Unidos, con reglas específicas.
        Acepta números en formato WhatsApp (sin +) y en formato internacional (con +)

        Args:
            phone (str): Número de teléfono a validar.

        Returns:
            bool: True si es válido, False en caso contrario.
        """
        if not phone:
            return False

        formatted_phone = phone

        # Formato WhatsApp: números que empiezan con el código de país sin +
        if not phone.startswith('+'):
            if (phone.startswith('1') and len(phone) == 11) or (phone.startswith('34') and len(phone) == 11):
                formatted_phone = f"+{phone}"
            else:
                return False  # Número sin + que no cumple con el formato esperado

        try:
            # Intenta analizar el número
            parsed = phonenumbers.parse(formatted_phone, None)

            # Verifica si el número es válido en general
            if not phonenumbers.is_valid_number(parsed):
                return False

            # Obtiene la región del número
            region = phonenumbers.region_code_for_number(parsed)

            # Verifica si la región está permitida
            if region not in PhoneNumberValidator.ALLOWED_REGIONS:
                return False

            national_number = str(parsed.national_number)

            # Reglas específicas para España
            if region == 'ES':
                if not national_number[0] in PhoneNumberValidator.VALID_ES_PREFIXES:
                    return False
                if len(national_number) != 9:  # Los números españoles tienen 9 dígitos
                    return False

            # Reglas específicas para Estados Unidos
            elif region == 'US':
                if len(national_number) != 10:  # Los números de USA tienen 10 dígitos
                    return False

            return True

        except NumberParseException:
            return False


    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Formatea el número de teléfono en formato internacional E.164.

        Args:
            phone (str): Número de teléfono a formatear.

        Returns:
            str: Número de teléfono en formato E.164.

        Raises:
            ValueError: Si el número no es válido.
        """
        if not phone.startswith("+"):
            phone = f"+{phone}"

        try:
            parsed = phonenumbers.parse(phone, None)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            else:
                raise ValueError("Número de teléfono inválido")
        except NumberParseException as e:
            raise ValueError(f"Error al analizar el número: {e}")

    @staticmethod
    def get_region(phone: str) -> str:
        """
        Obtiene la región asociada al número de teléfono.

        Args:
            phone (str): Número de teléfono.

        Returns:
            str: Código de la región (ej. 'US', 'ES').

        Raises:
            ValueError: Si el número no es válido.
        """
        if not phone.startswith("+"):
            phone = f"+{phone}"

        try:
            parsed = phonenumbers.parse(phone, None)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.region_code_for_number(parsed)
            else:
                raise ValueError("Número de teléfono inválido")
        except NumberParseException as e:
            raise ValueError(f"Error al analizar el número: {e}")

    @staticmethod
    def get_example_number(region: str = "US") -> str:
        """
        Devuelve un número de teléfono de ejemplo válido para una región específica.

        Args:
            region (str): Código de la región (ej. 'US', 'ES').

        Returns:
            str: Número de teléfono de ejemplo en formato E.164.
        """
        example_number = phonenumbers.example_number(region)
        return phonenumbers.format_number(example_number, phonenumbers.PhoneNumberFormat.E164)


class MessageFormatter:
    @staticmethod
    def get_message(template_key: str, language: Language, **kwargs) -> str:
        """Gets a message template in the specified language and formats it"""
        template = RESPONSE_TEMPLATES[language][template_key]
        return template.format(**kwargs)

    @staticmethod
    def get_error(error_key: str, language: Language) -> str:
        """Gets an error message in the specified language"""
        return ERROR_MESSAGES[language][error_key]


def is_valid_email(email: str) -> bool:
    """Validates email format"""
    return bool(re.match(VALIDATION_RULES["EMAIL_RULES"]["PATTERN"], email))


def is_service_available(service_name: str) -> bool:
    """Checks if a service is available"""
    """Checks if a service is available"""
    import asyncio

    return asyncio.run(check_service_status(service_name))

class MessageFormatter:
    @staticmethod
    def get_message(template_key: str, language: Language, **kwargs) -> str:
        """Gets a message template in the specified language and formats it"""
        # Implement message template retrieval and formatting
        pass

    @staticmethod
    def get_error(error_key: str, language: Language) -> str:
        """Gets an error message in the specified language"""
        # Implement error message retrieval
        pass
