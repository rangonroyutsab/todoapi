import logging

from django.conf import settings

from .clients import AIClient, AIServiceTimeout, AIServiceUnavailable, GeminiClient
from .exceptions import GatewayTimeout, ServiceUnavailable

logger = logging.getLogger(__name__)


class TaskDescriptionService:
    """Service for generating AI-powered task descriptions."""

    def __init__(self, client: AIClient):
        self._client = client

    def generate(self, title: str, description: str = "") -> str:
        """Generate or refine a task description using AI.

        Args:
            title: The task title.
            description: Optional existing description to refine.

        Returns:
            The generated description text.

        Raises:
            GatewayTimeout: If the AI service times out.
            ServiceUnavailable: If the AI service is unavailable or returns errors.
        """
        prompt = self._build_prompt(title, description)
        try:
            return self._client.generate_content(prompt)
        except AIServiceTimeout as exc:
            raise GatewayTimeout(detail=str(exc)) from exc
        except AIServiceUnavailable as exc:
            raise ServiceUnavailable(detail=str(exc)) from exc

    @staticmethod
    def _build_prompt(title: str, description: str) -> str:
        """Build the AI prompt based on whether a description already exists."""
        if not description:
            prompt = (
                f"Generate a two-sentence description for a task "
                f"with the title: '{title}'."
            )
        else:
            prompt = (
                f"Refine and rewrite the following task description into "
                f"exactly two sentences. Task title: '{title}'. "
                f"Existing description: '{description}'."
            )

        prompt += (
            "\n\nCRITICAL: The response MUST be exactly two sentences long. "
            "Do not include markdown formatting, prefix, or other text. "
            "Return ONLY the description."
        )
        return prompt


def get_description_service() -> TaskDescriptionService:
    """Factory function — the composition root.

    Reads the API key from Django settings and creates a concrete
    GeminiClient. This is the only place where the concrete client
    is instantiated.

    Raises:
        ServiceUnavailable: If the Gemini API key is not configured.
    """
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        logger.error("GEMINI_API_KEY is not configured.")
        raise ServiceUnavailable()

    client = GeminiClient(api_key=api_key)
    return TaskDescriptionService(client=client)
