import re
from enum import Enum
from typing import Dict

from .attendance import AttendanceManager
from .claude import generate_claude_response
from .message_coordinator import process_message
from .service_status import check_service_status

__all__ = [
    "AttendanceManager",
    "generate_claude_response",
    "process_message",
]


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


class PhoneNumberValidator:
    @staticmethod
    def validate_phone(phone: str, region: Region = Region.ES) -> bool:
        """Validates phone number format for specific region"""
        pattern = PHONE_PATTERNS[region]["pattern"]
        return bool(re.match(pattern, phone))

    @staticmethod
    def format_phone(phone: str, region: Region = Region.ES) -> str:
        """Formats phone number according to region standard"""
        # Remove all non-numeric characters
        cleaned = re.sub(r"[^\d]", "", phone)

        if region == Region.US:
            if len(cleaned) == 10:
                return f"+1{cleaned}"
            elif len(cleaned) == 11 and cleaned.startswith("1"):
                return f"+{cleaned}"

        elif region == Region.ES:
            if len(cleaned) == 9:
                return f"+34{cleaned}"
            elif len(cleaned) == 11 and cleaned.startswith("34"):
                return f"+{cleaned}"

        raise ValueError(f"Invalid phone number format for region {region}")

    @staticmethod
    def get_example_number(region: Region = Region.ES) -> str:
        """Returns an example valid phone number for the region"""
        return PHONE_PATTERNS[region]["example"]


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
