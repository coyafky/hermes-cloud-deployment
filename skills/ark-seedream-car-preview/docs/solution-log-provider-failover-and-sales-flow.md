# 车膜预览 Skill 模块化与销售流程验证日志

## 背景

原始 `ark-seedream-car-preview` skill 的核心能力是：

- 根据客户实车图生成车膜改色预览图。
- 根据 `color_assets.json` 查询色号、色名、HEX、Lab 和 preview 色卡图。
- 组装严格 prompt，要求只改变车身贴膜区域，保留车辆、场景、轮毂、车窗、车牌、光影和背景。
- 调用图像生成 API，保存生成结果，并可通过 OpenClaw 回传飞书或微信。

这套逻辑本身是正确的，但原始实现存在一个结构性问题：`scripts/gen.py` 承担了太多职责，且 provider 逻辑和业务逻辑耦合在一起。某个中转站不可用时，整个生成链路容易失效。

## 要解决的问题

本次要解决的核心问题不是简单替换一个 API，而是让 skill 变成可迭代、可测试、可替换 provider 的项目结构。

主要目标：

- 不再依赖单一中转站。
- 不再把 Ark 或某个效果较差的模型作为固定备选。
- 通过多个 OpenAI-compatible 生图 API 中转站做轮询备选。
- 保证每一个小逻辑都可以单独验证。
- 保持车膜业务逻辑稳定：客户实车图第一张，preview 色卡图第二张，HEX/Lab 只做辅助标注。
- 用真实“车主 + 销售”场景跑通验证，而不只是跑代码单元测试。

## 关键判断

### 1. provider 是外部通道，不应该进入业务核心

车膜预览业务真正稳定的部分是：

```text
客户实车图 = 唯一车辆主体依据
preview 色卡图 = 主要颜色和膜面依据
HEX / Lab / 色名 = 辅助识别字段
provider = 可替换的外部生图通道
```

所以 provider 不应该被写死在 `gen.py` 里。业务层只需要调用统一接口：

```python
provider.generate(
    prompt=prompt,
    refs=[vehicle_image, color_swatch],
    size=size,
    quality=quality,
    response_format=response_format,
)
```

### 2. 单文件脚本不利于定位问题

原始 `gen.py` 大约 600 多行，混合了：

- 命令行参数解析
- API key 读取
- 色卡资产查询
- prompt 构建
- 本地图片转 data URL
- provider 调用
- 图片 URL/base64 保存
- dry-run 输出

这种结构能跑，但一旦失败，很难快速判断是色卡查询错、prompt 错、图片引用错、provider 挂了，还是结果保存失败。

### 3. provider failover 比“备用模型”更重要

本次不再把字节模型作为备选，因为效果不满足业务要求。更合理的备选方式是多个高质量生图模型的 OpenAI-compatible 中转站：

```text
4sapi_primary -> apiyi_primary -> xinghu_third -> relay_backup
```

如果第一个 API 挂了，router 记录失败原因，然后尝试下一个 provider。

## 新文件结构

本次新增了模块化包：

```text
wrap_preview/
  __init__.py
  models.py
  config.py
  paths.py
  text.py
  assets.py
  refs.py
  prompt.py
  validation.py
  output.py
  service.py
  providers/
    __init__.py
    base.py
    errors.py
    openai_compatible.py
    router.py
```

职责拆分：

| 文件 | 职责 |
| --- | --- |
| `scripts/gen.py` | CLI 薄入口，只解析参数并调用 service |
| `wrap_preview/assets.py` | 查询 `color_assets.json`，自动补全色名、色号、HEX、材质和 preview 色卡图 |
| `wrap_preview/prompt.py` | 生成严格车膜改色 prompt |
| `wrap_preview/refs.py` | 处理本地路径、URL、data URL，保证参考图可上传 |
| `wrap_preview/validation.py` | 校验必须有客户车图和 preview 色卡图 |
| `wrap_preview/output.py` | 保存 provider 返回的 URL 或 base64 图片 |
| `wrap_preview/providers/openai_compatible.py` | OpenAI-compatible 生图 API 适配器 |
| `wrap_preview/providers/router.py` | provider 轮询与失败切换 |
| `wrap_preview/service.py` | 编排完整生成流程 |

## Provider 配置

新增 `.env.example` 作为模板：

```bash
WRAP_PROVIDER_CHAIN=4sapi_primary,apiyi_primary,xinghu_third,relay_backup

WRAP_PROVIDER_4SAPI_PRIMARY_BASE_URL=https://4sapi.com/v1
WRAP_PROVIDER_4SAPI_PRIMARY_API_KEY=replace-with-a-new-rotated-key
WRAP_PROVIDER_4SAPI_PRIMARY_MODEL=gpt-image-2
WRAP_PROVIDER_4SAPI_PRIMARY_AUTH_SCHEME=bearer

WRAP_PROVIDER_RELAY_BACKUP_BASE_URL=https://backup.example.com/v1
WRAP_PROVIDER_RELAY_BACKUP_API_KEY=replace-with-backup-key
WRAP_PROVIDER_RELAY_BACKUP_MODEL=gpt-image-2

WRAP_PROVIDER_XINGHU_THIRD_BASE_URL=https://xinghuapi.com/v1
WRAP_PROVIDER_XINGHU_THIRD_API_KEY=replace-with-xinghu-key
WRAP_PROVIDER_XINGHU_THIRD_MODEL=gpt-image-2
WRAP_PROVIDER_RELAY_BACKUP_AUTH_SCHEME=bearer
```

真实 key 不写入 `.env.example`，而是放入本地 `.env.local`。

同时更新 `.gitignore`：

```text
.env.local
.local.json
skills/*/.env.local
skills/*/.local.json
```

这样本机可以跑，仓库不会提交私密配置。

## 安全处理

测试过程中发现真实 API key 曾经被写入 `.env.example`。这是不安全的，因为 `.env.example` 通常会被提交到仓库。

处理方式：

- 将真实 key 迁移到 `.env.local`。
- 将 `.env.example` 恢复为占位符。
- 确认 `.env.local` 被 git ignore。
- 在配置读取逻辑中支持 `.env.local` 覆盖 `.env`。
- 增加占位符识别，`replace-with-*` 不会被误判为有效 API key。

建议：已经暴露过的 key 应在中转站后台重新生成并替换。

## 测试覆盖

新增标准库 `unittest` 测试，不依赖 pytest：

```text
tests/test_assets.py
tests/test_prompt.py
tests/test_validation.py
tests/test_refs.py
tests/test_output.py
tests/test_provider_router.py
tests/test_service_dry_run.py
```

测试重点：

- `A-001` 能查到正确色卡资产。
- prompt 必须包含“preview 色卡图”“不要只根据文字、HEX 或 Lab 猜测颜色”“只换膜色，不换车”。
- 缺少车图或色卡图时必须拒绝生成。
- 本地图片能转成 data URL。
- base64 返回能保存成本地图片。
- provider router 能在第一个 provider 失败后切换到第二个。
- service dry-run 能正确返回车图 + 色卡图两个 refs。

验证命令：

```bash
python3 -m unittest discover -s tests -v
```

结果：

```text
Ran 10 tests
OK
```

## 真实销售流程验证

### 流程模板

模拟真实销售对话：

```text
车主：我想看看这辆车贴某个色号的效果。
销售：收到，我用你的实车图 + 指定色号 preview 色卡图生成上车效果。
Hermes：提取 vehicle_ref 和 asset_id。
gen.py：查资产 -> 自动追加色卡图 -> 构建 prompt -> 调 provider -> 保存图片。
```

### 测试 1：宝马 M4 + A-001 宝马阿布扎比蓝

输入图片：

```text
/Users/fkycoya/Documents/MySecondBrain/1-Projects/01-Company-Work/picture设计/5-1海报30张图片/汽车image/image/宝马 M4 双门.jpeg
```

命令：

```bash
python3 scripts/gen.py \
  --vehicle-ref "/Users/fkycoya/Documents/MySecondBrain/1-Projects/01-Company-Work/picture设计/5-1海报30张图片/汽车image/image/宝马 M4 双门.jpeg" \
  --asset-id A-001 \
  --out-dir /tmp/bmw-m4-wrap-preview-test-b64 \
  --quality high \
  --response-format b64_json
```

结果：

```text
provider: 4sapi_primary
color_asset: A-001 宝马阿布扎比蓝
output: /private/tmp/bmw-m4-wrap-preview-test-b64/image-1.png
```

### 测试 2：宝马 M4 + B-120 玉米黄

命令：

```bash
python3 scripts/gen.py \
  --vehicle-ref "/Users/fkycoya/Documents/MySecondBrain/1-Projects/01-Company-Work/picture设计/5-1海报30张图片/汽车image/image/宝马 M4 双门.jpeg" \
  --asset-id B-120 \
  --out-dir /tmp/bmw-m4-wrap-preview-b120 \
  --quality high
```

结果：

```text
provider: 4sapi_primary
color_asset: B-120 玉米黄
output: /private/tmp/bmw-m4-wrap-preview-b120/image-1.png
```

### 测试 3：小鹏 P7 + B-121 沙丘黄

输入图片：

```text
/Users/fkycoya/Documents/MySecondBrain/1-Projects/01-Company-Work/picture设计/5-1海报30张图片/汽车image/image/小鹏p7.jpeg
```

命令：

```bash
python3 scripts/gen.py \
  --vehicle-ref "/Users/fkycoya/Documents/MySecondBrain/1-Projects/01-Company-Work/picture设计/5-1海报30张图片/汽车image/image/小鹏p7.jpeg" \
  --asset-id B-121 \
  --out-dir /tmp/xpeng-p7-wrap-preview-b121 \
  --quality high
```

结果：

```text
provider: 4sapi_primary
color_asset: B-121 沙丘黄
outputs:
  /private/tmp/xpeng-p7-wrap-preview-b121/image-1.png
  /private/tmp/xpeng-p7-wrap-preview-b121/image-2.png
```

本次模型返回了两张图，说明 provider 可能返回多张 base64 结果，`output.py` 的保存逻辑能够正确处理。

## 踩坑与修正

### 1. `response_format=url` 生成成功但下载失败

首次真实生成时，provider 返回 URL，但下载图片阶段出现：

```text
HTTP Error 403: Forbidden
```

判断：某些中转站返回的临时 URL 可能需要额外鉴权或权限限制。

修正：

- 默认响应格式改为 `b64_json`。
- 让 provider 直接返回 base64 图片，脚本本地解码保存。
- 在 `SKILL.md` 和架构文档中记录原因。

### 2. 测试不应该依赖 pytest

初始测试用 pytest，但服务器环境未安装 pytest。

修正：

- 改成 Python 标准库 `unittest`。
- 保证 skill 在干净 Python 环境中也能自检。

### 3. 占位符不应该算有效 key

`.env.example` 中的 `replace-with-backup-key` 曾被 dry-run 显示为 `has_api_key=True`。

修正：

- 增加 `is_placeholder_value()`。
- `replace-with-*`、`todo`、`changeme`、`your-api-key` 不算有效密钥。

### 4. 图片生成成功不等于已经发到飞书

历史会话 `20260603_182942_2007d583` 中，B-121 沙丘黄效果图已经生成成功：

```text
generated file:
  /Users/fkycoya/tmp/ark-seedream-car-preview-2026-06-03-18-30-55/image-1.jpeg
```

但第一次发送时调用的是 Hermes `send_message`：

```json
{
  "action": "send",
  "target": "origin",
  "message": "... MEDIA:/Users/fkycoya/tmp/ark-seedream-car-preview-2026-06-03-18-30-55/image-1.jpeg"
}
```

工具返回：

```text
Unknown platform: origin
```

判断：当时失败的不是图像生成，而是飞书投递目标解析。`origin` 没有被 `send_message` 当作可用 platform 识别，所以消息没有真正发出。后续再次回复中把 `MEDIA:/absolute/path` 放进当前飞书会话的普通回复正文，Feishu gateway 才把它作为媒体渲染出来。

修正：

- `gen_and_send.py` 保留 OpenClaw `message send --media <path>` 方式，明确传 `--channel feishu` 与具体 `--target`。
- 新增 `--dry-run-send`，用于验证飞书发送命令结构，不打扰真实会话。
- 每次真实投递都必须检查发送工具返回值；不要只看到 `files` 或 `MEDIA:` 字段就判断已经发送成功。
- 在 Hermes 当前会话内直接回复时，可使用 `MEDIA:/absolute/path`；在脚本或后台任务中，应走显式 OpenClaw media send。

### 5. 星狐重新接入为第三 provider

星狐可作为 OpenAI-compatible 图像中转站接入。根据星狐示例代码，代码侧 `model` 仍使用 `gpt-image-2`；“A龙虾专属 Image”是星狐账号/分组侧的专属通道标签，不应写进 `model` 字段。

本次重新接入为第三 provider：

```text
4sapi_primary -> apiyi_primary -> xinghu_third -> relay_backup
```

配置：

```bash
WRAP_PROVIDER_XINGHU_THIRD_BASE_URL=https://xinghuapi.com/v1
WRAP_PROVIDER_XINGHU_THIRD_MODEL=gpt-image-2
WRAP_PROVIDER_XINGHU_THIRD_AUTH_SCHEME=bearer
WRAP_PROVIDER_XINGHU_THIRD_REQUEST_STYLE=refs_array
WRAP_PROVIDER_XINGHU_THIRD_WATERMARK=true
WRAP_PROVIDER_XINGHU_THIRD_RESPONSE_FORMAT=url
```

本地 dry-run 已确认：

```text
provider: xinghu_third
base_url: https://xinghuapi.com/v1
model: gpt-image-2
request_style: refs_array
response_format: url
has_api_key: true
```

首次真实请求返回：

```text
503 model_not_found: No available channel for model gpt-image-2 under current group
```

判断：这不是本地路由错误，也不是鉴权失败。后续按星狐 SDK 示例补齐了请求形态差异：`extra_body.image` 等价的顶层 `image` 数组、`watermark=true`、以及星狐 provider 单独使用 `response_format=url`。如果它返回失败，router 会记录失败并继续尝试后续 provider。

## 当前结论

本次重构后，skill 已经从“大脚本 + 单 provider”变成了：

```text
模块化业务逻辑
+ OpenAI-compatible provider 适配器
+ provider chain 轮询
+ dry-run 可检查
+ unittest 可自检
+ 真实销售流程已验证
```

最重要的稳定规则仍然保持：

```text
客户实车图必须存在。
preview 色卡图必须存在。
客户实车图必须排第一。
preview 色卡图必须排第二。
HEX / Lab 只是辅助，不允许纯数值生图。
只换膜色，不换车。
输出图必须保持客户原始车辆照片的宽高比例；像素尺寸可不同，但不能变成方图或其他错误比例。
```

## 后续建议

1. 轮换已经暴露过的 4sapi key。
2. 持续验证 4sapi、APIYi、星狐三个真实中转站的 failover 网络路径。
3. 把销售流程测试固定成脚本，例如 `scripts/run_sales_flow_smoke.py`。
4. 增加输出质检字段，例如是否返回多张图、是否保留车辆主体、是否发生背景大幅变化。
5. 后续如接入飞书机器人，可直接调用 `wrap_preview.service.generate_wrap_preview()`，而不是重新拼命令行。
