from __future__ import annotations

import logging


class LiteLLMOptionalAwsWarningFilter(logging.Filter):
    """Suppress LiteLLM warnings for optional AWS streaming dependencies."""

    SUPPRESSED_FRAGMENTS = (
        "could not pre-load bedrock-runtime response stream shape",
        "could not pre-load sagemaker-runtime response stream shape",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage().lower()
        return not any(fragment in message for fragment in self.SUPPRESSED_FRAGMENTS)


_FILTER = LiteLLMOptionalAwsWarningFilter()
_INSTALLED = False


def suppress_litellm_optional_aws_warnings() -> None:
    """Install a narrow filter for noisy LiteLLM AWS optional-dependency warnings."""
    global _INSTALLED
    if _INSTALLED:
        return

    logger_names = (
        "LiteLLM",
        "litellm",
        "litellm.common_utils",
        "litellm.utils",
    )
    for name in logger_names:
        logging.getLogger(name).addFilter(_FILTER)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(_FILTER)

    _INSTALLED = True
