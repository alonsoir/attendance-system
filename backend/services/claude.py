import logging
import json
import asyncio
import aiohttp
from aiohttp import ServerTimeoutError, ClientConnectionError
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

    async def generate_response(self, student_name: str, message: str = None) -> dict:
        """
        Generate a response from Claude about a student's attendance situation.

        Args:
            student_name (str): Name of the student
            message (str, optional): Custom message. Defaults to None.

        Returns:
            dict: Response with structure {
                "sensitivity": int (1-10),
                "response": str,
                "likely_to_be_on_leave_tomorrow": bool,
                "reach_out_tomorrow": bool
            }
        """
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
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are an Attendance Officer who embodies sensitivity, responsiveness, empathy, and practicality.
                            Analyze the message and provide a response in valid JSON format with this exact structure:
                            {
                                "sensitivity": <integer between 1-10>,
                                "response": <your empathetic response>,
                                "likely_to_be_on_leave_tomorrow": <boolean>,
                                "reach_out_tomorrow": <boolean>
                            }
                            Where sensitivity is rated:
                            1-3: Routine matters (being late, minor delays)
                            4-6: Moderate concerns (doctor appointments, planned absences)
                            7-8: Significant issues (illness, family matters)
                            9-10: Critical situations (emergencies, serious health issues)"""
                        },
                        {
                            "role": "user",
                            "content": message or f"Why is {student_name} not present in class today?"
                        }
                    ],
                },
                timeout=30
            ) as response:
                try:
                    claude_response = await response.json()
                    logger.debug(f"Raw Claude response: {claude_response}")

                    if 'error' in claude_response:
                        error_msg = claude_response['error'].get('message', 'Unknown error from Claude')
                        return self._create_error_response(f"Error: {error_msg}")

                    content = claude_response.get('content', [{}])[0].get('text', '{}')
                    logger.debug(f"Extracted content: {content}")

                    try:
                        parsed_response = json.loads(content)
                        logger.debug(f"Parsed response: {parsed_response}")

                        if isinstance(parsed_response, dict) and "sensitivity" in parsed_response:
                            return parsed_response
                        else:
                            logger.error(f"Invalid response structure: {parsed_response}")
                            return self._create_error_response("Error: Invalid response structure")

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error: {e}, content: {content}")
                        return self._create_error_response(f"Error: Failed to parse response - {str(e)}")

                except Exception as e:
                    logger.error(f"Error processing Claude response: {e}")
                    return self._create_error_response(f"Error: Failed to process response - {str(e)}")

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
        """Create a response with default values and given error message."""
        return {
            "sensitivity": 5,
            "response": error_message,
            "likely_to_be_on_leave_tomorrow": False,
            "reach_out_tomorrow": False
        }

# Global instance
claude_service = ClaudeService.get_instance()

# Backwards compatibility function
async def generate_claude_response(student_name: str, message: str = None) -> dict:
    """
    Backwards compatibility function for existing code.
    Use ClaudeService.get_instance().generate_response() for new code.
    """
    return await claude_service.generate_response(student_name, message)
