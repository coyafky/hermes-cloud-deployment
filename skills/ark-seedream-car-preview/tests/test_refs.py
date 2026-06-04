from pathlib import Path
import tempfile
import unittest

from wrap_preview.refs import normalize_refs


class RefTests(unittest.TestCase):
    def test_normalize_refs_keeps_urls_and_encodes_local_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "card.png"
            image.write_bytes(b"fake-png")

            refs = normalize_refs(["https://example.com/car.png", image.as_posix()])

        self.assertEqual(refs[0], "https://example.com/car.png")
        self.assertTrue(refs[1].startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
