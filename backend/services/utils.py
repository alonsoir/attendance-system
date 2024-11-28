from enum import Enum
from typing import Dict
import re


class Language(str, Enum):
    EN_US = "en-US"
    ES_ES = "es-ES"


class Region(str, Enum):
    US = "US"
    ES = "ES"


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


class PhoneNumberValidator:
    @staticmethod
    def validate_phone(phone: str, region: Region = Region.ES) -> bool:
        """Validates phone number format for specific region"""
        pattern = PHONE_PATTERNS[region]["pattern"]
        return bool(re.match(pattern, phone))

    @staticmethod
    def format_phone(phone: str, region: Region = Region.ES) -> str:
        """Formats phone number according to region standard"""
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
        # Implement message template retrieval and formatting
        pass

    @staticmethod
    def get_error(error_key: str, language: Language) -> str:
        """Gets an error message in the specified language"""
        # Implement error message retrieval
        pass
