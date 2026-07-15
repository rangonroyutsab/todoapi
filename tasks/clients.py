import logging
from typing import Protocol

import requests

logger = logging.getLogger(__name__)

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.1-flash-lite:generateContent"
)
DEFAULT_TIMEOUT_SECONDS = 10


# ── Client Exceptions ──────────────────────────────────────────────


class AIClientError(Exception):
    """Base exception for AI client errors."""


class AIServiceUnavailable(AIClientError):
    """The AI service returned an error or invalid response."""


class AIServiceTimeout(AIClientError):
    """The AI service request timed out."""


# ── Protocol (abstraction for DIP) ─────────────────────────────────


class AIClient(Protocol):
    """Protocol defining the interface for AI content generation clients."""

    def generate_content(self, prompt: str) -> str: ...


# ── Concrete Implementation ────────────────────────────────────────


class GeminiClient:
    """Client for the Google Gemini generative-language API."""

    def __init__(self, api_key: str, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self._api_key = api_key
        self._timeout = timeout

    def generate_content(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the generated text.

        Raises:
            AIServiceTimeout: If the request times out.
            AIServiceUnavailable: If the API returns an error or invalid data.
        """
        headers = {"x-goog-api-key": self._api_key}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = requests.post(
                GEMINI_API_URL,
                headers=headers,
                json=payload,
                timeout=self._timeout,
            )
        except requests.exceptions.Timeout:
            logger.error("Gemini API request timed out.")
            raise AIServiceTimeout("The request to the AI service timed out.")
        except requests.exceptions.RequestException as err:
            logger.exception("Gemini API connection error: %s", type(err).__name__)
            raise AIServiceUnavailable(
                "Could not connect to the AI service."
            ) from err

        if response.status_code != 200:
            logger.error("Gemini API returned error %s", response.status_code)
            raise AIServiceUnavailable(
                "Failed to generate description from AI service."
            )

        return self._parse_response(response.json())

    def _parse_response(self, data: dict) -> str:
        """Extract generated text from the Gemini response payload."""
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if not text:
                raise ValueError("Empty AI output")
            return text
        except (KeyError, IndexError, ValueError) as exc:
            logger.error("Failed to parse Gemini response structure.")
            raise AIServiceUnavailable(
                "Received invalid response format from AI service."
            ) from exc
