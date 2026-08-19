"""
Prompt Security and Input Sanitization Guardrail.

Protects LLMs from prompt injection, system prompt exfiltration,
and out-of-domain malicious payloads.
"""

import re


class PromptSecurityError(Exception):
    """Raised when an adversarial prompt injection or dangerous input is detected."""



# Patterns typically used in prompt injection / jailbreaking
INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|directions)",
    r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|prompts|directions)",
    r"you\s+are\s+now\s+(in\s+)?(dan|jailbreak|developer|unrestricted)\s+mode",
    r"reveal\s+(your\s+)?(system\s+prompt|hidden\s+instructions|base\s+prompt)",
    r"print\s+(your\s+)?(system\s+prompt|hidden\s+instructions)",
    r"forget\s+(your\s+)?(rules|instructions|guardrails)",
    r"system\s*:\s*override",
    r"<\s*script\s*>",
]


class PromptGuard:
    """Sanitizes user input and detects prompt injection attempts."""

    def __init__(self, max_chars: int = 4000):
        self.max_chars = max_chars

    def sanitize(self, user_query: str) -> str:
        """
        Validates input length, strips control chars, and screens for injection.

        Args:
            user_query: Raw user query string.

        Returns:
            Sanitized query.

        Raises:
            PromptSecurityError: If an injection attempt or malicious payload is detected.
        """
        if not user_query or not user_query.strip():
            raise PromptSecurityError("Query cannot be empty.")

        if len(user_query) > self.max_chars:
            raise PromptSecurityError(
                f"Query length ({len(user_query)}) exceeds maximum allowed ({self.max_chars} chars)."
            )

        # Check for injection patterns
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, user_query, flags=re.IGNORECASE):
                raise PromptSecurityError(
                    "Potential prompt injection / adversarial instruction detected. "
                    "Please submit a valid business or data inquiry."
                )

        # Clean non-printable control characters except standard whitespace
        cleaned = "".join(ch for ch in user_query if ch == "\n" or ch == "\t" or (32 <= ord(ch) <= 126) or ord(ch) > 127)

        return cleaned.strip()


prompt_guard = PromptGuard()
