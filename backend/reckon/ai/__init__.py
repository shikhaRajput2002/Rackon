from django.conf import settings

from reckon.ai.anthropic_provider import AnthropicProvider
from reckon.ai.base import AIProvider
from reckon.ai.fake import FakeProvider

PROVIDERS = {
    "fake": FakeProvider,
    "anthropic": AnthropicProvider,
}


def get_provider() -> AIProvider:
    """The single place the app decides which AI is behind the feature."""
    provider_class = PROVIDERS.get(settings.AI_PROVIDER)
    if provider_class is None:
        raise ValueError(f"Unknown AI_PROVIDER '{settings.AI_PROVIDER}'. Expected one of: {sorted(PROVIDERS)}")
    return provider_class()
