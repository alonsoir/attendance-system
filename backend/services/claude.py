import asyncio
import json
import logging

import aiohttp
from aiohttp import ClientConnectionError, ServerTimeoutError

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


class ClaudeService:
    _instance = None
    settings = get_settings()
    _session = None
    _session_lock = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if not self.__initialized:
            self.__initialized = True
            if self._session_lock is None:
                self._session_lock = asyncio.Lock()
            if self._session is None:
                self._session = None

    @staticmethod
    def get_instance():
        if ClaudeService._instance is None:
            ClaudeService._instance = ClaudeService()
        return ClaudeService._instance

    async def close_session(self):
        """Close session with proper locking."""
        async with self._session_lock:
            if self._session:
                await self._session.close()
                self._session = None

    # Quien me invoca???
    async def generate_response_when_tutor(
        self, message_from_tutor: str = None
    ) -> dict:
        """Generate response from Claude about student attendance when tutor sends a message."""
        if self._session is None:
            async with self._session_lock:
                if self._session is None:
                    self._session = aiohttp.ClientSession()

        try:
            async with self._session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1024,
                    "system": """
                    You are an Attendance Officer who embodies sensitivity, responsiveness, empathy, and practicality.

IMPORTANT: You MUST detect the language of the incoming message and RESPOND IN THE SAME LANGUAGE. 
For example:
- If the message is in English -> respond in English
- If the message is in Spanish -> respond in Spanish

Your response must be ONLY a valid JSON object with this exact structure:
{
    "sensitivity": <integer between 1-10>,
    "response": <your empathetic response in the SAME LANGUAGE as the input>,
    "likely_to_be_on_leave_tomorrow": <boolean>,
    "reach_out_tomorrow": <boolean>
}

Sensitivity levels:
1-3: Routine matters (being late, minor delays)
4-6: Moderate concerns (doctor appointments, planned absences)
7-8: Significant issues (illness, family matters)
9-10: Critical situations (emergencies, serious health issues)

DO NOT include any text before or after the JSON object.""",
                    "messages": [{"role": "user", "content": message_from_tutor}],
                },
                timeout=30,
            ) as response:
                try:
                    claude_response = await response.json()
                    logger.debug(f"Raw Claude response: {claude_response}")

                    if "error" in claude_response:
                        error_msg = claude_response["error"].get(
                            "message", "Unknown error from Claude"
                        )
                        return self._create_error_response(f"Error: {error_msg}")

                    if "content" in claude_response:
                        try:
                            content = claude_response["content"][0]["text"].strip()
                            # Intentar encontrar el inicio del JSON
                            json_start = content.find("{")
                            if json_start != -1:
                                content = content[json_start:]
                            parsed_response = json.loads(content)
                            logger.debug(f"Parsed response: {parsed_response}")
                            return parsed_response
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON parse error: {e}, content: {content}")
                            return self._create_error_response(
                                f"Error: Failed to parse response - {str(e)}"
                            )
                    else:
                        logger.error(f"Invalid response structure: {claude_response}")
                        return self._create_error_response(
                            "Error: Invalid response structure"
                        )

                except Exception as e:
                    logger.error(f"Error processing Claude response: {e}")
                    return self._create_error_response(
                        f"Error: Failed to process response - {str(e)}"
                    )

        except ServerTimeoutError as e:
            logger.error(f"Timeout error calling Claude API: {e}")
            return self._create_error_response(f"Error: {str(e)}")
        except ClientConnectionError as e:
            logger.error(f"Connection error calling Claude API: {e}")
            return self._create_error_response(f"Error: {str(e)}")
        except AttributeError as e:
            logger.error(f"Attribute error calling Claude API: {e}")
            return self._create_error_response(f"Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling Claude API: {e}")
            return self._create_error_response(f"Error: {str(e)}")

    # Quien me invoca???
    def _create_error_response(self, error_message: str) -> dict:
        """Create error response with default values."""
        return {
            "sensitivity": 5,
            "response": error_message,
            "likely_to_be_on_leave_tomorrow": False,
            "reach_out_tomorrow": False,
        }

    # Quien me invoca???
    async def generate_response_when_college(
        self, student_name: str, message: str = None
    ) -> dict:
        """Generate response from Claude about student attendance when college sends a message."""
        logger.debug(
            f"Generating response for college when student {student_name} is absent: {message}"
        )
        if self._session is None:
            async with self._session_lock:
                if self._session is None:
                    self._session = aiohttp.ClientSession()

        try:
            async with self._session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1024,
                    "system": """You are an Attendance Officer who embodies sensitivity, responsiveness, empathy, and practicality.

IMPORTANT: You MUST detect the language of the incoming message and RESPOND IN THE SAME LANGUAGE. 
For example:
- If the message is in English -> respond in English
- If the message is in Spanish -> respond in Spanish

Your response must be ONLY a valid JSON object with this exact structure:
{
    "sensitivity": <integer between 1-10>,
    "response": <your empathetic response in the SAME LANGUAGE as the input>,
    "likely_to_be_on_leave_tomorrow": <boolean>,
    "reach_out_tomorrow": <boolean>
}

Sensitivity levels:
1-3: Routine matters (being late, minor delays)
4-6: Moderate concerns (doctor appointments, planned absences)
7-8: Significant issues (illness, family matters)
9-10: Critical situations (emergencies, serious health issues)

DO NOT include any text before or after the JSON object.""",
                    "messages": [{"role": "user", "content": message}],
                },
                timeout=30,
            ) as response:
                try:
                    claude_response = await response.json()
                    logger.debug(f"Raw Claude response: {claude_response}")

                    if "error" in claude_response:
                        error_msg = claude_response["error"].get(
                            "message", "Unknown error from Claude"
                        )
                        return self._create_error_response(f"Error: {error_msg}")

                    content = claude_response.get("content", [{}])[0].get("text", "{}")
                    logger.debug(f"Extracted content: {content}")

                    try:
                        parsed_response = json.loads(content)
                        logger.debug(f"Parsed response: {parsed_response}")

                        if (
                            isinstance(parsed_response, dict)
                            and "sensitivity" in parsed_response
                        ):
                            return parsed_response
                        else:
                            logger.error(
                                f"Invalid response structure: {parsed_response}"
                            )
                            return self._create_error_response(
                                "Error: Invalid response structure"
                            )

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error: {e}, content: {content}")
                        return self._create_error_response(
                            f"Error: Failed to parse response - {str(e)}"
                        )

                except Exception as e:
                    logger.error(f"Error processing Claude response: {e}")
                    return self._create_error_response(
                        f"Error: Failed to process response - {str(e)}"
                    )

        except ServerTimeoutError as e:
            logger.error(f"Timeout error calling Claude API: {e}")
            return self._create_error_response(f"Error: {str(e)}")
        except ClientConnectionError as e:
            logger.error(f"Connection error calling Claude API: {e}")
            return self._create_error_response(f"Error: {str(e)}")
        except AttributeError as e:
            logger.error(f"Attribute error calling Claude API: {e}")
            return self._create_error_response(f"Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling Claude API: {e}")
            return self._create_error_response(f"Error: {str(e)}")

    def _create_error_response(self, error_message: str) -> dict:
        """Create error response with default values."""
        return {
            "sensitivity": 5,
            "response": error_message,
            "likely_to_be_on_leave_tomorrow": False,
            "reach_out_tomorrow": False,
        }


# Global instance
claude_service = ClaudeService.get_instance()


async def generate_claude_response(student_name: str, message: str = None) -> dict:
    """Backwards compatibility function."""
    return await claude_service.generate_response(student_name, message)
