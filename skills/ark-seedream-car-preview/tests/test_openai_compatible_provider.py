import unittest

from wrap_preview.models import ProviderConfig
from wrap_preview.providers.openai_compatible import OpenAICompatibleProvider


class RecordingProvider(OpenAICompatibleProvider):
    def __init__(self, config):
        super().__init__(config)
        self.last_url = ""
        self.last_payload = {}

    def _post_json(self, url: str, payload: dict) -> dict:
        self.last_url = url
        self.last_payload = payload
        return {"data": [{"url": "https://example.com/image.png"}]}


class OpenAICompatibleProviderTests(unittest.TestCase):
    def test_refs_array_request_style_sends_all_refs(self):
        provider = RecordingProvider(
            ProviderConfig(
                name="apiyi_primary",
                base_url="https://api.apiyi.com/v1",
                api_key="key",
                request_style="refs_array",
            )
        )

        provider.generate(
            prompt="p",
            refs=["vehicle-ref", "swatch-ref"],
            size="auto",
            quality="high",
            response_format="b64_json",
        )

        self.assertEqual(provider.last_payload["image"], ["vehicle-ref", "swatch-ref"])
        self.assertEqual(provider.last_payload["response_format"], "b64_json")
        self.assertNotIn("watermark", provider.last_payload)

    def test_xinghu_refs_array_can_submit_vehicle_and_swatch_refs(self):
        provider = RecordingProvider(
            ProviderConfig(
                name="xinghu_third",
                base_url="https://xinghuapi.com/v1",
                api_key="key",
                request_style="refs_array",
                watermark=True,
                response_format="url",
            )
        )

        provider.generate(
            prompt="p",
            refs=["vehicle-ref", "swatch-ref"],
            size="1024x1024",
            quality="high",
            response_format="b64_json",
        )

        self.assertEqual(provider.last_payload["image"], ["vehicle-ref", "swatch-ref"])
        self.assertTrue(provider.last_payload["watermark"])
        self.assertEqual(provider.last_payload["response_format"], "url")

    def test_single_image_request_style_matches_xinghu_extra_body_shape(self):
        provider = RecordingProvider(
            ProviderConfig(
                name="xinghu_third",
                base_url="https://xinghuapi.com/v1",
                api_key="key",
                request_style="single_image",
                watermark=True,
                response_format="url",
            )
        )

        provider.generate(
            prompt="p",
            refs=["vehicle-ref", "swatch-ref"],
            size="1024x1024",
            quality="high",
            response_format="b64_json",
        )

        self.assertEqual(provider.last_url, "https://xinghuapi.com/v1/images/generations")
        self.assertEqual(provider.last_payload["model"], "gpt-image-2")
        self.assertEqual(provider.last_payload["image"], "vehicle-ref")
        self.assertTrue(provider.last_payload["watermark"])
        self.assertEqual(provider.last_payload["response_format"], "url")


if __name__ == "__main__":
    unittest.main()
