import unittest

from wrap_preview.models import WrapPreviewRequest
from wrap_preview.prompt import build_prompt


class PromptTests(unittest.TestCase):
    def test_prompt_preserves_wrap_preview_constraints(self):
        prompt = build_prompt(
            WrapPreviewRequest(
                color_name="宝马阿布扎比蓝",
                color_code="A-001",
                color_value="#4B6687",
                finish="PET改色膜",
            )
        )

        self.assertIn("preview 色卡图", prompt)
        self.assertIn("不要只根据文字、HEX 或 Lab 猜测颜色", prompt)
        self.assertIn("只换膜色，不换车", prompt)
        self.assertIn("Same vehicle", prompt)


if __name__ == "__main__":
    unittest.main()
