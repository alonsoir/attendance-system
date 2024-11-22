import asyncio
import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import aiohttp

from backend.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

PHONE_PATTERNS = {
    "ES": r"^\+34[6789]\d{8}$",  # Móviles y fijos españoles
    "US": r"^\+1\d{10}$",  # Números de EE.UU.
}


def validate_phone_number(phone: str) -> bool:
    """Valida el formato del número de teléfono según patrones configurados."""
    return any(re.match(pattern, phone) for pattern in PHONE_PATTERNS.values())


class MessageProvider(str, Enum):
    CALLMEBOT = "callmebot"
    META = "meta"
    MOCK = "mock"


class WhatsAppService:
    _instance: Optional["WhatsAppService"] = None
    _http_client: Optional[aiohttp.ClientSession] = None

    def __new__(cls, *args, **kwargs):
        """Crea una única instancia del servicio."""
        if cls._instance is None:
            cls._instance = super(WhatsAppService, cls).__new__(cls)
            cls._instance.__initialized = False  # Control interno de inicialización
        return cls._instance

    def __init__(
        self,
        meta_api_key: Optional[str] = None,
        callback_token: Optional[str] = None,
        provider: MessageProvider = MessageProvider.MOCK,
    ):
        if hasattr(self, "__initialized"):
            return  # Evitar re-inicializar el Singleton

        self.meta_api_key = meta_api_key or getattr(settings, "META_API_KEY", "")
        self.callback_token = callback_token or getattr(
            settings, "WHATSAPP_CALLBACK_TOKEN", "test_token"
        )
        self.provider = provider
        self.is_mock = not (self.meta_api_key and self.callback_token) or provider == MessageProvider.MOCK

        if self.is_mock:
            logger.warning("WhatsApp service running in MOCK mode - messages will be logged but not sent")
        logger.info(f"WhatsApp service initialized with provider: {self.provider}")

        self.__initialized = True  # Marcar como inicializado

    @classmethod
    async def init_service(cls):
        """Inicializa el cliente HTTP si no está ya inicializado."""
        if cls._http_client is None or cls._http_client.closed:
            cls._http_client = aiohttp.ClientSession()
            logger.info("WhatsAppService HTTP client initialized.")

    @classmethod
    async def close_service(cls):
        """Cierra el cliente HTTP si está abierto."""
        if cls._http_client and not cls._http_client.closed:
            await cls._http_client.close()
            cls._http_client = None
            logger.info("WhatsAppService HTTP client closed.")

    async def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Envía un mensaje a través del proveedor configurado."""
        if not validate_phone_number(phone):
            raise ValueError(f"Invalid phone number: {phone}")
        if not self._http_client:
            raise RuntimeError("WhatsAppService must be initialized with `init_service()` before usage.")

        try:
            if self.is_mock:
                return await self._send_mock_message(phone, message)
            if self.provider == MessageProvider.CALLMEBOT:
                return await self._send_callmebot_message(phone, message)
            elif self.provider == MessageProvider.META:
                return await self._send_meta_message(phone, message)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error while sending message: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error while sending message: {e}")
            raise Exception("Network Error")

    async def _send_mock_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Simula el envío de un mensaje y registra la acción."""
        logger.info(f"MOCK message to {phone}: {message}")
        await asyncio.sleep(0.5)
        return {
            "status": "success",
            "mock": True,
            "phone": phone,
            "message": message,
            "timestamp": str(datetime.now()),
        }

    async def _send_callmebot_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Envía un mensaje a través de CallMeBot."""
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={self.meta_api_key}"
        logger.info(f"Sending message to {phone} via CallMeBot")
        async with self._http_client.get(url) as response:
            response.raise_for_status()
            return {
                "status": "success",
                "provider": "callmebot",
                "response": await response.text(),
            }

    async def _send_meta_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Envía un mensaje usando la API oficial de Meta."""
        logger.warning("Meta WhatsApp API not implemented yet")
        raise NotImplementedError("Meta WhatsApp API not implemented yet")

    async def verify_callback(self, token: str) -> bool:
        """Verifica el token de callback."""
        return token == self.callback_token if not self.is_mock else True

    def get_status(self) -> Dict[str, Any]:
        """Devuelve el estado actual del servicio."""
        return {
            "mode": "mock" if self.is_mock else "live",
            "provider": self.provider,
            "features_enabled": {
                "sending": bool(self.meta_api_key),
                "callbacks": bool(self.callback_token),
            },
        }
