# Car Wrap Preview Prompt

## Structured template

请以客户提供的实车照片为基础进行高真实度效果图生成，并严格参考客户选定的车膜色卡。

任务目标：

将客户所选车膜颜色，真实、自然地呈现在客户车辆上，输出一张接近实拍效果的贴膜预览图，方便客户确认上车后的视觉效果。

执行要求：

- 以客户车辆原图为唯一主体基础，保持车辆品牌、车型、车身结构、轮毂、车灯、车窗、角度、透视关系、拍摄场景、背景环境完全不变。
- 严格参考提供的车膜色卡颜色进行贴膜效果呈现，优先依据色卡实物颜色、色号、LAB信息，还原准确色彩。
- 仅修改需要贴膜覆盖的区域颜色与材质表现，不要改变未贴膜区域。
- 保留原车照片中的真实光影、反射 、高光、阴影、金属质感、环境倒影，使结果看起来像真实施工后的实拍照片。
- 不要改变车辆外观套件，不要修改车牌、轮胎、玻璃、门把手、车灯、内饰，不要新增或删除任何部件。
- 不要美化成概念图，不要插画风，不要海报风，不要夸张渲染，必须是写实商业修图效果。
- 输出结果需干净、高清、自然，适合作为给客户确认的施工预览图。

颜色参考说明：

- LAB编号：{color_code}

约束重点：

- 只换膜色，不换车。
- 只做真实贴膜效果，不做重设计。
- 保持原图构图、背景、光线、细节一致。
- 最终效果必须像同一辆车在同一地点贴完膜后重新拍摄的照片。

## Recommended suffix

Same vehicle, same location, same composition, same camera angle, same lens perspective, same background, same lighting direction, same reflections, same wheel position, same trim details. Only the wrap-covered painted panels may change color and finish. Everything else must remain identical to the original photo. Realistic automotive photography, subtle commercial retouching only, no redesign, no extra objects, no text, no watermark beyond provider default.
