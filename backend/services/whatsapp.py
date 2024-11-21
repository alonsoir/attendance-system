import asyncio
import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict
from typing import Optional

import aiohttp

from backend.core.config import get_settings

# from backend.services import AttendanceManager

logger = logging.getLogger(__name__)

settings = get_settings()
def validate_phone_number(phone: str) -> bool:
    """
    Valida el formato del número de teléfono.
    Acepta formatos:
    - España: +34XXXXXXXXX (9 dígitos después del +34)
    - Estados Unidos: +1XXXXXXXXXX (10 dígitos después del +1)
    """
    # Patrones para diferentes países
    patterns = {
        "ES": r"^\+34[6789]\d{8}$",  # Móviles y fijos españoles
        "US": r"^\+1\d{10}$",  # Números de EE. UU.
    }

    # Verificar contra todos los patrones
    return any(re.match(pattern, phone) for pattern in patterns.values())


class MessageProvider(str, Enum):
    CALLMEBOT = "callmebot"
    META = "meta"
    MOCK = "mock"


class WhatsAppService:
    def __init__(
        self,
        meta_api_key: Optional[str] = None,
        callback_token: Optional[str] = None,
        provider: MessageProvider = MessageProvider.MOCK,
    ):
        self.meta_api_key = meta_api_key or getattr(settings, "META_API_KEY", "")
        self.callback_token = callback_token or getattr(
            settings, "WHATSAPP_CALLBACK_TOKEN", "test_token"
        )
        self.provider = provider
        self.is_mock = (
            not (self.meta_api_key and self.callback_token)
            or provider == MessageProvider.MOCK
        )

        if self.is_mock:
            logger.warning(
                "WhatsApp service running in MOCK mode - messages will be logged but not sent"
            )

        logger.info(f"WhatsApp service initialized with provider: {self.provider}")

    async def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de WhatsApp usando el proveedor configurado.
        """
        # Validar el número de teléfono primero
        if not validate_phone_number(phone):
            raise ValueError(f"Invalid phone number. FORMAT!: {phone}")
        try:
            if self.is_mock:
                return await self._send_mock_message(phone, message)
            if self.provider == MessageProvider.CALLMEBOT:
                return await self._send_callmebot_message(phone, message)
            elif self.provider == MessageProvider.META:
                return await self._send_meta_message(phone, message)
            else:
                raise ValueError(f"Proveedor no soportado: {self.provider}")

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise

    async def _send_mock_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Simula el envío de un mensaje y lo registra.
        """
        logger.info(f"MOCK WhatsApp message to {phone}: {message}")
        await asyncio.sleep(0.5)  # Simular latencia de red

        return {
            "status": "success",
            "mock": True,
            "phone": phone,
            "message": message,
            "timestamp": str(datetime.now()),
        }

    async def _send_callmebot_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje usando CallMeBot.
        """
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={self.meta_api_key}"
        logger.info(f"Enviando mensaje a {phone} via CallMeBot")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return {
                    "status": "success",
                    "provider": "callmebot",
                    "response": await response.text(),
                }

    async def _send_meta_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje usando la API oficial de Meta/WhatsApp.
        """
        # Implementar cuando tengamos acceso a la API oficial
        raise NotImplementedError("Meta WhatsApp API not implemented yet")

    async def handle_message(self, message_data: dict) -> Dict[str, Any]:
        """
        Procesa un mensaje entrante de WhatsApp.
        """
        from backend.services.message_coordinator import process_message

        return await process_message(
            message_data=message_data, send_response_callback=self.send_message
        )

    async def verify_callback(self, token: str) -> bool:
        """
        Verifica el token de callback de WhatsApp.
        """
        if self.is_mock:
            return True
        return token == self.callback_token

    def get_status(self) -> Dict[str, Any]:
        """
        Devuelve el estado actual del servicio.
        """
        return {
            "mode": "mock" if self.is_mock else "live",
            "provider": self.provider,
            "features_enabled": {
                "sending": bool(self.meta_api_key),
                "callbacks": bool(self.callback_token),
            },
        }

# Funciones de conveniencia para mantener compatibilidad con código existente
async def send_whatsapp_message(phone: str, message: str) -> Dict[str, Any]:
    return await whatsapp_service.send_message(phone, message)


async def handle_whatsapp_message(message_data: dict) -> Dict[str, Any]:
    return await whatsapp_service.handle_message(message_data)

# Instancia global del servicio
whatsapp_service = WhatsAppService(provider=getattr(settings, "WHATSAPP_PROVIDER", MessageProvider.CALLMEBOT))