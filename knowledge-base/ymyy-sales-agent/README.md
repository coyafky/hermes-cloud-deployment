# 有膜有漾 Sales Agent 知识库

本目录是给 Hermes/飞书内部销售助手使用的结构化知识库。主数据文件是 `ymyy-service-manual.jsonl`，每行一条 JSON 知识记录。

## 文件说明

- `ymyy-service-manual.jsonl`：RAG 主库，包含品牌、产品、售后、销售边界。
- `queries.md`：验收问题和期望答案。
- `source-audit.md`：PDF 抽取、图片参数页和人工校对说明。

## 入库规则

- 一款产品、一条 SOP、一个品牌事实各自成条，不按 PDF 页机械切片。
- 每条必须保留 `source` 和 `source_page`；无法对应页码的内部规则用 `source_page: null`。
- 产品参数写入 `specs`；销售话术写入 `sales_talk`；不能对外承诺的限制写入 `guardrails`。
- 价格、活动、库存、门店政策和施工排期不写入固定知识库。
- 回答参数类问题时必须返回来源页，例如“来源：有膜有漾服务手册 p.8”。

## 推荐检索策略

1. 用户问题先分类：品牌介绍、产品推荐、参数查询、异议处理、售后保养、价格政策。
2. 参数查询优先检索 `title`、`id`、`category`、`specs`。
3. 推荐类问题同时检索 `customer_fit`、`selling_points`、`sales_talk`。
4. 售后类问题优先检索 `aftercare_sop`。
5. 涉及价格、活动、库存时，直接命中 `ymyy-sales-script-price-policy` 并提醒以门店最新政策为准。

## 飞书常用入口建议

- “帮我推荐车膜”
- “客户嫌贵怎么说”
- “生成跟进话术”
- “查某个套餐参数”
- “施工后注意事项怎么发客户”

## 后续维护

- 当产品手册更新时，新增条目优先，不覆盖旧条目；确认旧条目失效后再标记下架。
- 对图片表格参数做二次校对时，在记录中追加 `verified_by` 和 `verified_at` 字段。
- 如果门店政策需要进入知识库，应单独放到门店政策库，并设置有效期。
