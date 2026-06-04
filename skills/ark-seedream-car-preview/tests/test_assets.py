from pathlib import Path
import unittest

from wrap_preview.assets import apply_color_asset
from wrap_preview.models import WrapPreviewRequest


class AssetTests(unittest.TestCase):
    def test_apply_color_asset_adds_swatch_and_prompt_fields(self):
        request = WrapPreviewRequest(asset_id="A-001")
        asset = apply_color_asset(request)

        self.assertEqual(asset["id"], "A-001")
        self.assertEqual(request.color_code, "A-001")
        self.assertIn("宝马阿布扎比蓝", request.color_name)
        self.assertEqual(request.color_value, "#4B6687")
        self.assertTrue(request.color_refs)
        self.assertTrue(Path(request.color_refs[0]).is_file())


if __name__ == "__main__":
    unittest.main()
