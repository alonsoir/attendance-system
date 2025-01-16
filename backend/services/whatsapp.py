import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import aiohttp
from aiohttp import ClientResponseError, ClientSession

from backend.core.config import get_settings
from backend.services.utils import MessageFormatter, PhoneNumberValidator

logger = logging.getLogger(__name__)

settings = get_settings()


class MessageProvider(str, Enum):
    CALLMEBOT = "callmebot"
    META = "meta"
    MOCK = "mock"


class WhatsAppService:
    _instance: Optional["WhatsAppService"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WhatsAppService, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        meta_api_key: Optional[str] = None,
        callback_token: Optional[str] = None,
        provider: MessageProvider = MessageProvider.MOCK,
    ):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.meta_api_key = meta_api_key or getattr(settings, "META_API_KEY", "")
        self.callback_token = callback_token or getattr(
            settings, "WHATSAPP_CALLBACK_TOKEN", "test_token"
        )
        self.provider = provider
        # self.is_mock = provider == MessageProvider.MOCK and self.meta_api_key is None and self.callback_token is not None
        self.is_mock = provider == MessageProvider.MOCK
        self._http_client: Optional[ClientSession] = None

        if self.is_mock:
            logger.warning(
                "WhatsApp service running in MOCK mode - messages will be logged but not sent"
            )
        logger.info(f"WhatsApp service initialized with provider: {self.provider}")

        self._initialized = True

    async def initialize(self):
        """Initializes the HTTP client."""
        if not self._http_client or self._http_client.closed:
            self._http_client = ClientSession()
            logger.info("WhatsAppService HTTP client initialized.")

    async def close(self):
        """Closes the HTTP client."""
        if self._http_client and not self._http_client.closed:
            await self._http_client.close()
            logger.info("WhatsAppService HTTP client closed.")

    async def get_message_from_tutor(
        self, webhook_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processes an incoming WhatsApp message from the Meta API webhook.

        Args:
            webhook_data (Dict[str, Any]): The data sent from the Meta API webhook.

        Returns:
            Dict[str, Any]: A response dictionary with the processed message details.
        """
        try:
            # Extract the relevant information from the webhook data
            phone_number = webhook_data["messaging"][0]["from"]
            message_text = webhook_data["messaging"][0]["text"]["body"]

            # Validate the phone number format
            if not PhoneNumberValidator.validate_phone(phone_number):
                return {
                    "status": "error",
                    "message": "Invalid phone number format",
                }

            # Process the message
            message = f"Hola, soy el tutor {phone_number}. {message_text}"
            logger.info(f"Received message from tutor {phone_number}: {message}")

            # TODO Save the message to the database or perform any other necessary actions
            # esto se tiene que hacer desde el método que tenga el control sobre el endpoint de whatsapp.
            # Return the processed message details
            return {
                "status": "success",
                "tutor_phone": phone_number,
                "message": message,
                "provider": "meta",
                "timestamp": str(datetime.now()),
            }

        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {str(e)}")
            return {
                "status": "error",
                "tutor_phone": "error_tutor_phone",
                "message": "Error processing message",
                "provider": "meta",
                "timestamp": str(datetime.now()),
            }

    async def save_message_to_database(phone: str, message: str):
        """
        Saves the received message to the database.
        """
        # Implement database storage logic here
        pass

    async def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Sends a message to the specified phone number."""
        if not PhoneNumberValidator.validate_phone(phone):
            raise ValueError(f"Invalid phone number: {phone}")
        if not self._http_client:
            raise RuntimeError("Service not initialized. Call `initialize()` first.")

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
            raise RuntimeError("An unexpected error occurred.")

    async def _send_mock_message(self, phone: str, message: str) -> Dict[str, Any]:
        logger.info(f"MOCK message to {phone}: {message}")
        await asyncio.sleep(0.5)
        return {
            "status": "success",
            "mock": True,
            "phone": phone,
            "message": message,
            "provider": "mock",
            "timestamp": str(datetime.now()),
        }

    async def _send_callmebot_message(self, phone: str, message: str) -> Dict[str, Any]:
        phone_formatted = PhoneNumberValidator.format_phone(phone)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone_formatted}&text={message}&apikey={self.meta_api_key}"
        logger.info(f"Sending message to {phone_formatted} via Meta WhatsApp API")
        logger.debug(f"URL: {url}")

        try:
            async with self._http_client.get(url) as response:
                response.raise_for_status()
                response_text = await response.text()
                return {
                    "status": "success",
                    "phone": phone_formatted,
                    "message": message,
                    "provider": "callmebot",
                    "response": response_text,
                    "timestamp": str(datetime.now()),
                }
        except ClientResponseError as e:
            logger.error(f"CallMeBot API response: {await response.text()}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response status: {response.status}")
            logger.debug(f"Exception text: {e.message}")
            raise

    async def _send_meta_message(self, phone: str, message: str) -> Dict[str, Any]:
        phone_formatted = PhoneNumberValidator.format_phone(phone)
        url = f"https://graph.facebook.com/v16.0/me/messages?access_token={self.meta_api_key}"
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_formatted,
            "text": {"body": message},
        }

        logger.info(f"Sending message to {phone_formatted} via Meta WhatsApp API")
        logger.debug(f"Payload: {payload}")
        logger.debug(f"URL: {url}")
        async with self._http_client.post(url, json=payload) as response:
            try:
                response.raise_for_status()
                response_json = await response.json()

                return {
                    "status": "success",
                    "phone": phone_formatted,
                    "message": message,
                    "provider": "meta",
                    "response": response_json,
                    "timestamp": str(datetime.now()),
                }
            except ClientResponseError as e:
                logger.error(f"Meta API response: {await response.text()}")
                logger.debug(f"Response headers: {response.headers}")
                logger.debug(f"Response status: {response.status}")
                logger.debug(f"Exception text: {e.message}")
                raise

    def get_status(self) -> Dict[str, Any]:
        """Returns the service status."""
        return {
            "mode": "mock" if self.is_mock else "live",
            "provider": self.provider,
            "features_enabled": {
                "sending": bool(self.meta_api_key),
                "callbacks": bool(self.callback_token),
            },
        }

    async def verify_callback(self, token: str) -> bool:
        """Verifies a callback token."""
        return token == self.callback_token if not self.is_mock else True
