from __future__ import annotations

from .models import WrapPreviewRequest
from .text import normalize_text


def build_prompt(request: WrapPreviewRequest) -> str:
    if request.prompt:
        return normalize_text(request.prompt)

    color_name = request.color_name or "客户选定车膜颜色"
    color_code = request.color_code or "未提供"
    color_value = request.color_value or "未提供"
    finish = request.finish or "未提供"
    description = request.description or "无"
    color_value_label = "HEX 辅助标注" if color_value.startswith("#") else "色值辅助标注"

    parts = [
        "请以客户提供的实车照片和 preview 色卡图为基础进行高真实度效果图生成，并严格采用图像参考完成车膜改色。",
        "任务目标：将客户所选车膜颜色，真实、自然地呈现在客户车辆上，输出一张接近实拍效果的贴膜预览图，方便客户确认上车后的视觉效果。",
        "图像参考使用规则：客户车辆照片是唯一车辆主体参考；preview 色卡图是目标车膜颜色和膜面视觉效果的主要颜色参考。不要只根据文字、HEX 或 Lab 猜测颜色，也不要用 Lab 重新换算目标颜色。",
        "执行要求：以客户车辆原图为唯一主体基础，保持车辆品牌、车型、车身结构、轮毂、车灯、车窗、角度、透视关系、拍摄场景、背景环境完全不变。",
        f"严格参考随输入图像提供的 preview 色卡图进行贴膜效果呈现，以色卡图的可见颜色为主，色号和数值只用于辅助识别。目标车膜颜色：{color_name}。色卡编号：{color_code}。{color_value_label}：{color_value}。材质说明：{finish}。补充描述：{description}。",
        "仅修改需要贴膜覆盖的区域颜色与材质表现，不要改变未贴膜区域。",
        "保留原车照片中的真实光影、反射、高光、阴影、金属质感、环境倒影，使结果看起来像真实施工后的实拍照片。",
        "如果该膜属于哑光、亮光、金属、珠光、变色龙等材质，请准确体现对应膜面质感。",
        "不要改变车辆外观套件，不要修改车牌、轮胎、玻璃、门把手、车灯、内饰，不要新增或删除任何部件。",
        "不要美化成概念图，不要插画风，不要海报风，不要夸张渲染，必须是写实商业修图效果。",
        "输出结果需干净、高清、自然，适合作为给客户确认的施工预览图。",
        "约束重点：只换膜色，不换车。只做真实贴膜效果，不做重设计。保持原图构图、背景、光线、细节一致。",
        "最终效果必须像同一辆车在同一地点贴完膜后重新拍摄的照片。",
        "Same vehicle, same location, same composition, same camera angle, same lens perspective, same background, same lighting direction, same reflections, same wheel position, same trim details. Only the wrap-covered painted panels may change color and finish. Everything else must remain identical to the original photo. Realistic automotive photography, no extra text.",
    ]
    return " ".join(parts)

