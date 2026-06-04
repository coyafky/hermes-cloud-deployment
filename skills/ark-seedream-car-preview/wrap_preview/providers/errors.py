from __future__ import annotations


class ProviderError(RuntimeError):
    pass


class ProviderConfigurationError(ProviderError):
    pass


class AllProvidersFailed(ProviderError):
    pass

