import tempfile
import unittest
from pathlib import Path

from PIL import Image

from wrap_preview.dimensions import assert_output_aspect_ratios, aspect_ratio_matches, read_image_dimensions


class DimensionsTests(unittest.TestCase):
    def test_reads_local_image_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "vehicle.png"
            Image.new("RGB", (640, 480), "white").save(path)

            self.assertEqual(read_image_dimensions(str(path)), (640, 480))

    def test_aspect_ratio_matches_accepts_same_ratio_different_pixels(self):
        self.assertTrue(aspect_ratio_matches((1448, 1086), (4032, 3024)))

    def test_assert_output_aspect_ratios_accepts_exact_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "generated.png"
            Image.new("RGB", (640, 480), "blue").save(path)

            self.assertEqual(assert_output_aspect_ratios([path], (640, 480)), [(640, 480)])

    def test_assert_output_aspect_ratios_accepts_same_ratio_without_modifying_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "generated.png"
            Image.new("RGB", (1448, 1086), "blue").save(path)

            self.assertEqual(assert_output_aspect_ratios([path], (4032, 3024)), [(1448, 1086)])

            with Image.open(path) as image:
                self.assertEqual(image.size, (1448, 1086))

    def test_assert_output_aspect_ratios_rejects_ratio_mismatch_without_modifying_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "generated.png"
            Image.new("RGB", (1024, 1024), "blue").save(path)

            with self.assertRaises(RuntimeError):
                assert_output_aspect_ratios([path], (640, 480))

            with Image.open(path) as image:
                self.assertEqual(image.size, (1024, 1024))


if __name__ == "__main__":
    unittest.main()
