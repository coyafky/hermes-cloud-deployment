import unittest

from wrap_preview.models import WrapPreviewRequest
from wrap_preview.service import generate_wrap_preview


class ServiceDryRunTests(unittest.TestCase):
    def test_service_dry_run_resolves_asset_and_refs(self):
        result = generate_wrap_preview(
            WrapPreviewRequest(
                dry_run=True,
                vehicle_refs=["https://example.com/customer-car.jpg"],
                asset_id="A-001",
                base_url="https://4sapi.com/v1",
            )
        )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["color_asset"]["id"], "A-001")
        self.assertEqual(len(result["refs"]), 2)
        self.assertEqual(result["refs"][0], "https://example.com/customer-car.jpg")
        self.assertTrue(result["refs"][1].endswith("A-001-measurement-4.png"))
        self.assertEqual(result["providers"][0]["base_url"], "https://4sapi.com/v1")
        self.assertIsNone(result["target_output_dimensions"])


if __name__ == "__main__":
    unittest.main()
