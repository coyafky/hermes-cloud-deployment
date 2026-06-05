# 车膜色卡数字化与 AI 改色预览详细架构

## 设计目标

这份架构图是在原有“车膜色卡数字化与 AI 改色渲染架构”基础上进一步展开，用来指导后续迁移到 Hermes `ymyy-sales-agent`。

核心目标：

- 色卡数据从实体测量到数字资产可追溯。
- 销售侧只需要上传车图和输入色号。
- Hermes 负责意图识别、文件处理、任务调度和回传。
- `wrap_preview` 保持为可测试的生图业务引擎。
- provider 作为可替换外部通道，支持多个 OpenAI-compatible API 轮询。
- 每次生成进入质检和反馈闭环，持续优化颜色资产和 prompt。

## 总体分层架构

```mermaid
flowchart TB
    subgraph layer1["① 色卡数字资产层"]
        physical["实体色卡\nA-001 / B-121 / PET"] --> measure["色差仪测量\nLab + 测量条件"]
        measure --> colorTool["Python 色彩工具\nLab -> RGB / HEX"]
        colorTool --> preview["标准 preview 色卡图\n色块 + 编码 + 参数"]
        preview --> assetLib["颜色资产库\ncolor_assets.json"]
        measure --> assetLib
    end

    subgraph layer2["② Hermes 销售智能体层"]
        feishu["飞书消息入口\n文本 + 图片附件"] --> mediaIn["媒体下载器\n图片落盘 / 对象存储"]
        mediaIn --> agent["ymyy-sales-agent\n意图识别 + 参数抽取"]
        agent --> tool["VehicleWrapPreview Tool\n结构化调用"]
    end

    subgraph layer3["③ 车膜预览业务引擎层"]
        service["wrap_preview.service\n流程编排"]
        assets["assets.py\n色号 / 色名查询"]
        validation["validation.py\n车图 + 色卡图校验"]
        refs["refs.py\n本地图转 data URL"]
        prompt["prompt.py\n只换膜色不换车"]
        output["output.py\n保存 URL / base64 图片"]
        service --> assets
        service --> validation
        service --> refs
        service --> prompt
        service --> output
    end

    subgraph layer4["④ 生图 Provider 层"]
        router["ProviderRouter\n按顺序轮询"]
        p1["4sapi_primary\nOpenAI-compatible"]
        p2["apiyi_primary\nOpenAI-compatible"]
        p3["xinghu_third\nOpenAI-compatible"]
        p4["relay_backup\nOpenAI-compatible"]
        p3["future_provider\nOpenAI-compatible"]
        router --> p1
    router --> p2
    router --> p3
    router --> p4
        router --> p3
    end

    subgraph layer5["⑤ 交付与反馈层"]
        result["改色预览图\nPNG / media token"]
        sendBack["飞书上传与回传\n图片 + 说明"]
        qa["人工质检\n可用 / 色差 / 变形"]
        feedback["反馈记录\n优化 prompt / 色卡资产"]
        version["更新资产库版本\ncolor_assets.json"]
        result --> sendBack
        result --> qa
        qa --> feedback
        feedback --> version
        version -.-> assetLib
    end

    assetLib --> assets
    tool --> service
    service --> router
    router --> result
```

## 销售运行时详细链路

```mermaid
sequenceDiagram
    participant Sales as 销售/车主
    participant Feishu as 飞书机器人
    participant Hermes as Hermes 网关
    participant Agent as ymyy-sales-agent
    participant Tool as VehicleWrapPreview Tool
    participant Engine as wrap_preview.service
    participant Asset as color_assets.json
    participant Provider as OpenAI-compatible Provider
    participant Store as 文件/对象存储

    Sales->>Feishu: 上传车辆图 + 输入色号 B-121
    Feishu->>Hermes: 消息事件 + 图片 file_key + 文本
    Hermes->>Store: 下载车辆图片到临时路径
    Store-->>Hermes: vehicle_ref
    Hermes->>Agent: 文本 + vehicle_ref + 会话上下文
    Agent->>Agent: 识别 vehicle_wrap_preview 意图
    Agent->>Agent: 抽取 asset_id = B-121
    Agent->>Tool: 调用结构化工具
    Tool->>Engine: WrapPreviewRequest
    Engine->>Asset: 查询 B-121
    Asset-->>Engine: 色名 / HEX / Lab / preview swatch
    Engine->>Engine: 校验 vehicle_ref + color_ref
    Engine->>Engine: 车图和色卡图转 data URL
    Engine->>Engine: 构建严格 prompt
    Engine->>Provider: prompt + image[0]车图 + image[1]色卡图
    Provider-->>Engine: b64_json 图片
    Engine->>Store: 解码并保存 PNG
    Store-->>Engine: result_files
    Engine-->>Tool: 生成结果 JSON
    Tool-->>Agent: 图片路径 + 色号摘要 + provider attempts
    Agent->>Hermes: 回传消息载荷
    Hermes->>Feishu: 上传图片并发送
    Feishu-->>Sales: 展示改色预览图
```

## 生图请求内部结构

```mermaid
flowchart LR
    subgraph input["输入材料"]
        vehicle["客户实车图\nvehicle_ref"]
        swatch["preview 色卡图\nasset.images.swatch"]
        fields["辅助字段\n色号 / 色名 / HEX / Lab / 材质"]
    end

    subgraph build["wrap_preview 构建请求"]
        order["固定顺序\nimage[0]=车图\nimage[1]=色卡图"]
        promptNode["Prompt\n只换膜色，不换车"]
        payload["OpenAI-compatible payload\nmodel / prompt / image / b64_json"]
    end

    subgraph provider["生图模型"]
        model["gpt-image-2 或同级模型\n通过中转站调用"]
    end

    subgraph output["输出"]
        b64["b64_json"]
        png["本地 PNG\nimage-1.png"]
        summary["JSON 摘要\nfiles / color_asset / provider_attempts"]
    end

    vehicle --> order
    swatch --> order
    fields --> promptNode
    order --> payload
    promptNode --> payload
    payload --> model
    model --> b64
    b64 --> png
    png --> summary
```

## Prompt 业务合同

生图 prompt 是业务合同，迁移和模块化时不能随意改变。当前核心约束如下：

```text
客户车辆照片是唯一车辆主体参考。
preview 色卡图是目标车膜颜色和膜面视觉效果的主要颜色参考。
不要只根据文字、HEX 或 Lab 猜测颜色，也不要用 Lab 重新换算目标颜色。
只修改需要贴膜覆盖的区域颜色与材质表现。
不要改变车型、轮毂、车灯、车窗、车牌、背景、角度、透视、光影。
不要生成概念图、插画、海报或重新设计效果。
最终效果必须像同一辆车在同一地点贴完膜后重新拍摄的照片。
```

对模型提交时，`HEX`、`Lab` 和色名只作为辅助字段，真正颜色依据必须是 `preview 色卡图`。

## 色卡资产生产链路

```mermaid
flowchart LR
    card["实体色卡\n色号 / 系列 / 材质"] --> lab["色差仪\nLab 测量"]
    lab --> record["测量记录\n光源 / 观察角 / 日期 / 场景"]
    record --> convert["Python 工具\nLab -> preview HEX"]
    convert --> swatch["preview 色卡 PNG\nassets/previews"]
    swatch --> review["人工确认\n接近实体色卡"]
    review --> asset["color_assets.json\nid / names / color / images / prompt"]

    asset --> query["query_color_assets.py\n销售查询 / Hermes 查询"]
    asset --> gen["wrap_preview.assets\n生成时自动加载"]
```

### 颜色资产字段

```mermaid
classDiagram
    class ColorAsset {
        id
        serial
        names.zh
        names.en
        names.aliases
        color.hex
        color.lab
        color.family
        material
        finish.prompt_label
        images.swatch
        prompt.color_name
        prompt.color_code
        prompt.color_value
        prompt.description
    }

    class Measurement {
        source
        card_db
        measurement_id
        measured_at
        preview_lab
    }

    class PreviewImage {
        swatch
        source_swatch_name
        match_strategy
    }

    ColorAsset --> Measurement
    ColorAsset --> PreviewImage
```

## Provider Failover 详细逻辑

```mermaid
flowchart TD
    start["开始生成"] --> load["读取 WRAP_PROVIDER_CHAIN"]
    load --> normalize["构建 ProviderConfig 列表"]
    normalize --> first["尝试 provider 1"]
    first --> ok1{"成功?"}
    ok1 -->|是| save["保存图片并返回"]
    ok1 -->|否| log1["记录失败原因"]
    log1 --> second["尝试 provider 2"]
    second --> ok2{"成功?"}
    ok2 -->|是| save
    ok2 -->|否| log2["记录失败原因"]
    log2 --> third["尝试 provider 3"]
    third --> ok3{"成功?"}
    ok3 -->|是| save
    ok3 -->|否| fail["全部失败\n返回 AllProvidersFailed"]

    save --> attempts["输出 provider_attempts"]
    fail --> attempts
```

Provider 配置例子：

```bash
WRAP_PROVIDER_CHAIN=4sapi_primary,apiyi_primary,xinghu_third,relay_backup

WRAP_PROVIDER_4SAPI_PRIMARY_BASE_URL=https://4sapi.com/v1
WRAP_PROVIDER_4SAPI_PRIMARY_API_KEY=...
WRAP_PROVIDER_4SAPI_PRIMARY_MODEL=gpt-image-2
WRAP_PROVIDER_4SAPI_PRIMARY_AUTH_SCHEME=bearer

WRAP_PROVIDER_RELAY_BACKUP_BASE_URL=https://backup.example.com/v1
WRAP_PROVIDER_RELAY_BACKUP_API_KEY=...
WRAP_PROVIDER_RELAY_BACKUP_MODEL=gpt-image-2

WRAP_PROVIDER_XINGHU_THIRD_BASE_URL=https://xinghuapi.com/v1
WRAP_PROVIDER_XINGHU_THIRD_API_KEY=...
WRAP_PROVIDER_XINGHU_THIRD_MODEL=gpt-image-2
WRAP_PROVIDER_XINGHU_THIRD_REQUEST_STYLE=refs_array
WRAP_PROVIDER_XINGHU_THIRD_WATERMARK=true
WRAP_PROVIDER_XINGHU_THIRD_RESPONSE_FORMAT=url
WRAP_PROVIDER_RELAY_BACKUP_AUTH_SCHEME=bearer
```

默认使用：

```text
response_format = b64_json
```

原因：某些中转站返回 URL 后可能在下载阶段出现 HTTP 403，`b64_json` 更适合自动化销售回传链路。

## 模块职责与可测试点

```mermaid
flowchart TB
    cli["scripts/gen.py\nCLI 入口"] --> service["service.py\n编排"]
    service --> assets["assets.py\n查色卡"]
    service --> validation["validation.py\n必填校验"]
    service --> refs["refs.py\n图片引用转换"]
    service --> prompt["prompt.py\n构建提示词"]
    service --> router["providers/router.py\n轮询"]
    router --> adapter["openai_compatible.py\nHTTP 请求"]
    service --> output["output.py\n保存图片"]

    assets -.测试.-> ta["test_assets.py"]
    validation -.测试.-> tv["test_validation.py"]
    refs -.测试.-> tr["test_refs.py"]
    prompt -.测试.-> tp["test_prompt.py"]
    router -.测试.-> tpr["test_provider_router.py"]
    output -.测试.-> to["test_output.py"]
    service -.测试.-> ts["test_service_dry_run.py"]
```

## 任务状态机

```mermaid
stateDiagram-v2
    [*] --> received: 收到飞书消息
    received --> waiting_image: 缺少车辆图
    received --> resolving_color: 有车图和色号
    waiting_image --> received: 用户补图
    resolving_color --> ambiguous_color: 多个候选
    ambiguous_color --> resolving_color: 用户确认色号
    resolving_color --> queued: 创建生图任务
    queued --> running: worker 开始执行
    running --> succeeded: provider 成功
    running --> provider_failed: 当前 provider 失败
    provider_failed --> running: 尝试下一个 provider
    provider_failed --> failed: 所有 provider 失败
    succeeded --> delivered: 飞书回传
    delivered --> reviewed: 销售/人工质检
    reviewed --> archived: 记录案例
    failed --> archived: 记录失败原因
```

## 质量反馈闭环

```mermaid
flowchart LR
    result["生成结果图"] --> salesReview["销售初审"]
    salesReview --> good["可直接发客户"]
    salesReview --> issue["存在问题"]

    issue --> colorIssue["颜色不准\n调整色卡描述"]
    issue --> shapeIssue["车辆结构变形\n加强 prompt 约束"]
    issue --> bgIssue["背景变化过大\n强化保持场景"]
    issue --> providerIssue["provider 不稳定\n调整 provider chain"]

    colorIssue --> assetUpdate["更新 color_assets.json\nprompt.description / finish"]
    shapeIssue --> promptUpdate["更新 prompt.py\n保持车辆结构"]
    bgIssue --> promptUpdate
    providerIssue --> configUpdate["更新 provider 配置"]

    assetUpdate --> version["资产版本记录"]
    promptUpdate --> version
    configUpdate --> version
    version --> smoke["销售流程 smoke test"]
    smoke --> result
```

## 错误兜底路径

| 错误类型 | 判断条件 | 用户话术 | 系统处理 |
| --- | --- | --- | --- |
| 缺少车图 | 没有 `vehicle_ref` | 需要先上传客户车辆图片 | 等待用户补图 |
| 缺少色卡 | 没有 `asset_id` 且没有 `color_ref` | 请提供色号或 preview 色卡图 | 返回参数缺失 |
| 色号不存在 | 资产库查不到 | 没有找到该色号，请确认 | 提供候选或让用户重输 |
| 色号模糊 | 命中多个相似资产 | 找到多个相似色号，请选择 | 返回候选列表 |
| provider 失败 | 当前 API 报错 | 正在切换备用通道 | router 尝试下一个 |
| provider 全挂 | 全部 provider 失败 | 当前生图通道不可用，请稍后重试 | 记录失败原因 |
| URL 下载 403 | URL 返回但无法下载 | 自动改用 base64 模式 | 默认使用 `b64_json` |

## Hermes 迁移后的落地点

```text
hermes-cloud-deployment/
  skills/
    ark-seedream-car-preview/
      wrap_preview/
      references/
      assets/
      scripts/

  knowledge-base/
    ymyy-sales-agent/
      vehicle-wrap-preview.md

  agents/
    ymyy-sales-agent/
      tools/
        vehicle_wrap_preview.py
      workflows/
        vehicle_wrap_preview_flow.py
```

建议保持 `wrap_preview` 作为独立业务引擎，Hermes 只通过工具包装层调用，不直接改内部 prompt、provider、色卡查询逻辑。

## 验收用例

| 用例 | 输入 | 期望 |
| --- | --- | --- |
| 宝马 M4 + A-001 | 车图 + `A-001` | 输出阿布扎比蓝预览图 |
| 宝马 M4 + B-120 | 车图 + `B-120` | 输出玉米黄预览图 |
| 小鹏 P7 + B-121 | 车图 + `B-121` | 输出沙丘黄预览图 |
| 缺少车图 | 仅 `B-121` | 返回补图提示 |
| 错误色号 | 车图 + `ZZ-999` | 返回色号不存在 |
| provider 失败 | primary API 故障 | 自动尝试 backup |

## 当前最重要的实现边界

不要把以下内容混进 `ymyy-sales-agent` 主逻辑：

- provider HTTP 细节
- base64 解码细节
- prompt 长文本
- 色卡 JSON fuzzy 查询细节
- 本地路径转 data URL 细节

这些都应该留在 `wrap_preview` 里。`ymyy-sales-agent` 只负责识别销售意图、准备结构化参数、调用工具、组织回传话术。
