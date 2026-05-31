class PolarisError(Exception):
    """Base exception for PolarisCore."""


class ConfigurationError(PolarisError):
    """Raised when the assistant is not configured correctly."""


class ProviderError(PolarisError):
    """Raised when an LLM provider fails."""
