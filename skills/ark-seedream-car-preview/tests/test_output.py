import base64
import tempfile
import unittest

from wrap_preview.output import extract_image_base64s, extract_image_urls, save_generated_images


class OutputTests(unittest.TestCase):
    def test_extracts_url_shapes(self):
        self.assertEqual(extract_image_urls({"data": [{"url": "https://example.com/a.png"}]}), ["https://example.com/a.png"])
        self.assertEqual(extract_image_urls({"output_url": "https://example.com/b.png"}), ["https://example.com/b.png"])

    def test_save_generated_images_from_base64(self):
        encoded = base64.b64encode(b"image-bytes").decode("ascii")
        response = {"data": [{"b64_json": encoded}]}
        with tempfile.TemporaryDirectory() as tmp:
            from pathlib import Path

            files, urls, base64_count = save_generated_images(response, Path(tmp))
            saved_bytes = files[0].read_bytes()

        self.assertEqual(extract_image_base64s(response), [encoded])
        self.assertEqual(urls, [])
        self.assertEqual(base64_count, 1)
        self.assertEqual(saved_bytes, b"image-bytes")


if __name__ == "__main__":
    unittest.main()
