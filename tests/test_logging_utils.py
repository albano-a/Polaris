import logging

from polaris_core.logging_utils import LiteLLMOptionalAwsWarningFilter


def test_litellm_optional_aws_warning_filter_suppresses_bedrock_warning():
    filter_ = LiteLLMOptionalAwsWarningFilter()
    record = logging.LogRecord(
        name="LiteLLM",
        level=logging.WARNING,
        pathname="common_utils.py",
        lineno=979,
        msg="litellm: could not pre-load bedrock-runtime response stream shape",
        args=(),
        exc_info=None,
    )

    assert filter_.filter(record) is False


def test_litellm_optional_aws_warning_filter_keeps_other_warnings():
    filter_ = LiteLLMOptionalAwsWarningFilter()
    record = logging.LogRecord(
        name="LiteLLM",
        level=logging.WARNING,
        pathname="providers.py",
        lineno=1,
        msg="important provider warning",
        args=(),
        exc_info=None,
    )

    assert filter_.filter(record) is True
