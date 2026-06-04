---
name: ark-seedream-car-preview
description: Hermes 车膜改色生图技能。根据客户实车图和车膜色卡资产库，查询色号/色名，组装稳定 prompt，通过多个 OpenAI-compatible 生图 API 中转站轮询生成真实车身贴膜预览图，并可通过 OpenClaw 回传到微信或飞书。
---

# Hermes 车膜改色预览生图

当用户、销售或 Hermes profile 需要根据“客户实车照片 + preview 色卡图”生成真实改色膜上车效果图时，使用本技能。

本技能面向车膜销售工作流，不是普通修图技能。核心目标是：只改变车身贴膜覆盖区域的颜色和膜面质感，保持车辆、场景、角度、轮毂、车灯、车牌、玻璃、背景和光影关系尽量不变，输出可发给客户确认的写实预览图。

## Hermes 触发条件

满足以下任一情况时触发：

- 客户上传实车图，并指定车膜色号，如 `A-001`、`D-325`
- 客户或销售说“帮我生成上车效果图”“改色预览”“贴膜效果图”“这个颜色上车看看”
- 输入中包含车膜中文名、英文名、色系或色卡图片
- Hermes 需要从本地 JSON 资产库查询颜色，并调用图像模型生成结果

不要在以下情况触发：

- 只是查询库存、报价、施工时间，不需要生成图片
- 用户要求完全重设计车辆外观、换车型、换轮毂、改装套件
- 用户没有提供实车图，且当前任务要求直接生成客户车辆效果图

## 输入结构

Hermes profile 推荐传入 JSON：

```json
{
  "task": "vehicle_wrap_preview",
  "vehicle_ref": "/absolute/path/to/customer-car.jpg",
  "color_asset_id": "A-001",
  "delivery": {
    "enabled": false,
    "channel": "openclaw-weixin",
    "target": ""
  },
  "generation": {
    "size": "auto",
    "quality": "high"
  }
}
```

当色号不在资产库中时，使用手动颜色字段：

```json
{
  "task": "vehicle_wrap_preview",
  "vehicle_ref": "/absolute/path/to/customer-car.jpg",
  "color_ref": "/absolute/path/to/color-card.jpg",
  "color_name": "勃艮第酒红",
  "color_code": "LPR803",
  "color_value": "#8B2942",
  "finish": "哑光",
  "description": "低饱和高级感，偏暖红酒色"
}
```

## 资产库

颜色资产库位于：

```text
{baseDir}/references/color_assets.json
```

资产库由 Lab 色卡表、`Card-color` 数据库中的 `preview_hex` 和本 skill 内置的 `assets/previews/` 色卡图生成。每个颜色资产包含：

- `id` / `serial`：稳定色号，例如 `A-001`
- `names.zh` / `names.en`：中英文名称
- `images.swatch`：preview 色卡图，路径应指向 `../assets/previews/...`，这是生图的主要颜色依据
- `color.hex`：色卡 PNG / `Card-color` 数据库标注的 HEX，只作为辅助标注和销售摘要字段
- `color.lab`：实体色卡 Lab 测量值，只作为辅助测量记录，不用来重新换算目标颜色
- `color.family`：色系
- `material` / `finish`：材质与膜面提示
- `prompt`：可直接注入生图脚本的结构化字段

查询颜色资产：

```bash
python3 {baseDir}/scripts/query_color_assets.py "宝马阿布扎比蓝"
python3 {baseDir}/scripts/query_color_assets.py A-001
python3 {baseDir}/scripts/query_color_assets.py 蓝色系 --limit 5
```

重建颜色资产库：

```bash
python3 {baseDir}/scripts/build_color_assets.py \
  --source /absolute/path/to/MGS-PET改色膜-飞书色卡画廊_色卡档案_全部色卡.xlsx \
  --preview-dir {baseDir}/assets/previews \
  --card-db /absolute/path/to/Card-color/data/color-lab.db
```

## 执行流程

1. 确认有客户实车图，作为 `--vehicle-ref`。
2. 优先用色号或色名查询 `references/color_assets.json`。
3. 如果查到资产，使用 `--asset-id`，由脚本自动注入色名、色号、HEX/Lab 辅助值、材质提示，并自动把资产库 `images.swatch` 作为 `--color-ref` 传入。
4. 如果查不到资产，必须使用 `--color-ref` 传入人工提供的色卡图；手动 HEX/Lab 只能作为辅助字段。
5. 调用 `gen.py` 生成图片；默认读取 `WRAP_PROVIDER_CHAIN` 或 `IMAGE_RELAY_BASE_URL`，通过多个 OpenAI-compatible 生图 API 中转站按顺序轮询。
6. 如果需要直接回传客户，调用 `gen_and_send.py`，它会把 provider 参数透传到生图脚本。
7. 输出结果返回给 Hermes，由 Hermes 决定展示、发送或进入人工质检。

## 只解析不生图

Hermes 路由或调试阶段可先 dry-run，检查最终 prompt 和引用图。命中资产时，`refs` 必须同时包含客户实车图和 preview 色卡图：

```bash
python3 {baseDir}/scripts/gen.py \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --dry-run
```

## 生成图片

使用资产库色号生成，默认走 provider chain：

```bash
python3 {baseDir}/scripts/gen.py \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --response-format b64_json \
  --quality high
```

上面命令会自动把 `references/color_assets.json` 中的 `images.swatch` 追加为色卡参考图，不需要销售手动传 `--color-ref`。

显式指定某个 OpenAI-compatible 中转站生成：

```bash
python3 {baseDir}/scripts/gen.py \
  --provider relay \
  --base-url "$IMAGE_RELAY_BASE_URL" \
  --model gpt-image-2 \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --size auto \
  --response-format b64_json \
  --quality high
```

OpenAI-compatible 路径会把客户车型图和资产库 preview 色卡图一起转成可上传的图片引用，并调用：

```text
{BASE_URL}/images/generations
```

其中车型图必须排在第一张，preview 色卡图必须排在第二张。色卡图仍是目标颜色和膜面视觉的主要依据，HEX/Lab 只进入 prompt 作为辅助识别字段。

默认 `response-format=b64_json`，这样模型结果会直接解码保存到本地，避免某些中转站返回的临时 URL 在下载阶段出现 403 权限问题。只有明确需要保留远程 URL 时，才手动传 `--response-format url`。

默认 `size=auto`，表示输出尺寸交给图像模型根据客户车型图的比例和内容决定；不要在飞书自动流程中固定为横版或方图。只有明确要做横版展示图、竖版海报或方图时，才手动传 `1536x1024`、`1024x1536` 或 `1024x1024`。

禁止回退到纯 HEX / Lab 生图：如果没有 `--asset-id` 命中的 `images.swatch`，就必须手动传 `--color-ref`。脚本会拒绝只有 `--color-value`、Lab 或文字描述的生图请求。

使用手动颜色字段生成：

```bash
python3 {baseDir}/scripts/gen.py \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --color-ref /absolute/path/to/color-card.jpg \
  --color-name "勃艮第酒红" \
  --color-code "LPR803" \
  --color-value "#8B2942" \
  --finish "哑光" \
  --description "低饱和高级感，偏暖红酒色" \
  --response-format b64_json
```

## 生成并回传

回传到微信：

```bash
python3 {baseDir}/scripts/gen_and_send.py \
  --channel openclaw-weixin \
  --target o9cq805uzekq7fioq4n5czimsgpk@im.wechat \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --message "这是基于实车图和色卡生成的车膜预览图"
```

回传到飞书：

```bash
python3 {baseDir}/scripts/gen_and_send.py \
  --channel feishu \
  --target oc_xxx \
  --provider relay \
  --base-url "$IMAGE_RELAY_BASE_URL" \
  --model gpt-image-2 \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --response-format b64_json \
  --message "这是基于实车图和色卡生成的车膜预览图"
```

## Prompt 约束

生图时必须遵守：

- 以客户车辆原图为唯一主体基础
- 只修改贴膜覆盖的车身漆面区域
- 保持车型、外观结构、轮毂、车灯、车窗、车牌、背景、角度、透视、光影和反射关系
- 色彩优先参考随输入传入的 preview 色卡图；`color.hex` 和 Lab 只作为辅助标注，不要只靠数值生成颜色，也不要用 Lab 重新换算目标颜色
- 膜面质感按资产库 `finish.prompt_hint` 或手动 `finish` 体现
- 不要生成概念车、海报、插画、棚拍大片或重新设计效果
- 不要新增文字、水印、装饰、配件或任何不在原图中的物体
- 给飞书/微信返回操作摘要时，说明本次生图依据为“客户车型图 + preview 色卡图”；色值字段可展示资产库 `color.hex`，可附带 Lab 辅助值；不要展示“明亮正黄”等非资产库实测描述

## 输出

`gen.py` 输出 JSON，关键字段包括：

- `prompt`：最终生图 prompt
- `files`：生成图片的本地绝对路径
- `relative_files`：相对路径
- `media_tokens`：OpenClaw 可识别媒体 token
- `color_asset`：本次命中的颜色资产摘要
- `provider`：本次成功调用的 provider 名称
- `provider_attempts`：provider 轮询尝试记录，失败时包含错误摘要
- `image_urls`：模型返回的原始图片 URL；如果 provider 返回 base64，脚本会直接解码保存到本地

## 依赖

- `python3`
- 一个或多个 OpenAI-compatible 生图 API 中转站
- provider chain 环境变量，例如：

```bash
WRAP_PROVIDER_CHAIN=4sapi_primary,relay_backup
WRAP_PROVIDER_4SAPI_PRIMARY_BASE_URL=https://4sapi.com/v1
WRAP_PROVIDER_4SAPI_PRIMARY_API_KEY=...
WRAP_PROVIDER_4SAPI_PRIMARY_MODEL=gpt-image-2
WRAP_PROVIDER_4SAPI_PRIMARY_AUTH_SCHEME=bearer

WRAP_PROVIDER_RELAY_BACKUP_BASE_URL=https://backup.example.com/v1
WRAP_PROVIDER_RELAY_BACKUP_API_KEY=...
WRAP_PROVIDER_RELAY_BACKUP_MODEL=gpt-image-2
WRAP_PROVIDER_RELAY_BACKUP_AUTH_SCHEME=bearer
```


## Hermes 注意事项

- 销售侧只需要收集实车图和色号/色名，不需要手写 prompt。
- 优先走 `--asset-id`，这样结果可追溯到资产库版本。
- 若用户对效果不满意，记录色号、生成图、反馈原因，再优化资产库中的 `finish` 或 `prompt.description`。
- 生图模型不是精确像素级编辑器，复杂遮挡、反光、局部贴膜边界仍建议人工复核。
