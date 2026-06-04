import unittest

from wrap_preview.models import WrapPreviewRequest
from wrap_preview.validation import validate_reference_images


class ValidationTests(unittest.TestCase):
    def test_validation_rejects_missing_vehicle_ref(self):
        with self.assertRaisesRegex(ValueError, "Missing --vehicle-ref"):
            validate_reference_images(WrapPreviewRequest(color_refs=["https://example.com/card.png"]))

    def test_validation_rejects_missing_color_ref(self):
        with self.assertRaisesRegex(ValueError, "Missing preview color-card image"):
            validate_reference_images(WrapPreviewRequest(vehicle_refs=["https://example.com/car.png"]))

    def test_validation_accepts_vehicle_and_color_refs(self):
        validate_reference_images(
            WrapPreviewRequest(
                vehicle_refs=["https://example.com/car.png"],
                color_refs=["https://example.com/card.png"],
            )
        )


if __name__ == "__main__":
    unittest.main()
