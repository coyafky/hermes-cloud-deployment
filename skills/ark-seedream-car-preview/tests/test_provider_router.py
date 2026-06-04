import unittest

from wrap_preview.models import ProviderConfig
from wrap_preview.providers.router import ProviderRouter


class StubProvider:
    calls = []

    def __init__(self, config):
        self.config = config

    def generate(self, **kwargs):
        StubProvider.calls.append(self.config.name)
        if self.config.name == "bad":
            from wrap_preview.providers.errors import ProviderError

            raise ProviderError("offline")
        return {"data": [{"url": "https://example.com/result.png"}]}


class ProviderRouterTests(unittest.TestCase):
    def test_router_fails_over(self):
        import wrap_preview.providers.router as router_module

        original_provider = router_module.OpenAICompatibleProvider
        router_module.OpenAICompatibleProvider = StubProvider
        self.addCleanup(setattr, router_module, "OpenAICompatibleProvider", original_provider)
        StubProvider.calls = []

        router = ProviderRouter(
            [
                ProviderConfig(name="bad", base_url="https://bad.example/v1", api_key="x"),
                ProviderConfig(name="good", base_url="https://good.example/v1", api_key="x"),
            ]
        )
        result = router.generate(prompt="p", refs=[], size="auto", quality="high", response_format="url")

        self.assertEqual(result.provider, "good")
        self.assertEqual(StubProvider.calls, ["bad", "good"])
        self.assertEqual([attempt.ok for attempt in result.attempts], [False, True])


if __name__ == "__main__":
    unittest.main()
