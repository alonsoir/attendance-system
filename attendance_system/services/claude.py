import asyncio
import aiohttp
from attendance_system.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def generate_claude_response(student_name: str) -> dict:
    prompt = {
        "role": "user",
        "content": f"You are an Attendance Officer who embodies sensitivity, responsiveness, empathy, and practicality. You asked the guardian of {student_name} for the reason why they are not present in the class...",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1024,
                "messages": [prompt],
            },
        ) as response:
            return await response.json()
