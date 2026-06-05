import unittest

from wrap_preview.config import load_named_provider


class ConfigTests(unittest.TestCase):
    def test_named_provider_accepts_legacy_apiyi_names(self):
        config = load_named_provider(
            {
                "APIYI_BASE_URL": "https://api.apiyi.com/v1",
                "APIYI_API_KEY": "legacy-key",
                "APIYI_MODEL": "gpt-image-2-all",
            },
            "apiyi_primary",
            "gpt-image-2",
        )

        self.assertIsNotNone(config)
        self.assertEqual(config.base_url, "https://api.apiyi.com/v1")
        self.assertEqual(config.api_key, "legacy-key")
        self.assertEqual(config.model, "gpt-image-2-all")

    def test_named_provider_accepts_legacy_4s_names(self):
        config = load_named_provider(
            {
                "FOURS_BASE_URL": "https://4sapi.com/v1",
                "4S_API_KEY": "legacy-key",
                "4S_MODEL": "gpt-image-2",
            },
            "4sapi_primary",
            "gpt-image-2-all",
        )

        self.assertIsNotNone(config)
        self.assertEqual(config.base_url, "https://4sapi.com/v1")
        self.assertEqual(config.api_key, "legacy-key")
        self.assertEqual(config.model, "gpt-image-2")

    def test_named_provider_accepts_legacy_xinghu_names(self):
        config = load_named_provider(
            {
                "XINGHU_BASE_URL": "https://xinghuapi.com/v1",
                "XINGHU_API_KEY": "legacy-key",
                "XINGHU_MODEL": "gpt-image-2",
                "XINGHU_REQUEST_STYLE": "single_image",
                "XINGHU_WATERMARK": "true",
                "XINGHU_RESPONSE_FORMAT": "url",
            },
            "xinghu_third",
            "gpt-image-2-all",
        )

        self.assertIsNotNone(config)
        self.assertEqual(config.base_url, "https://xinghuapi.com/v1")
        self.assertEqual(config.api_key, "legacy-key")
        self.assertEqual(config.model, "gpt-image-2")
        self.assertEqual(config.request_style, "single_image")
        self.assertTrue(config.watermark)
        self.assertEqual(config.response_format, "url")

    def test_xinghu_defaults_to_refs_array_request_style(self):
        config = load_named_provider(
            {
                "XINGHU_BASE_URL": "https://xinghuapi.com/v1",
                "XINGHU_API_KEY": "legacy-key",
            },
            "xinghu_third",
            "gpt-image-2",
        )

        self.assertIsNotNone(config)
        self.assertEqual(config.request_style, "refs_array")


if __name__ == "__main__":
    unittest.main()
