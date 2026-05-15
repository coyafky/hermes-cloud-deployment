# Sales Agent Acceptance Queries

## 1. 新车怕剐蹭

**Query:** 客户新买车，怕剐蹭，预算中等，推荐什么？

**Expected behavior:** 推荐隐形车衣方向，可主推中端或中高端车衣，并追问车型、预算、露天停车/高速情况。不得直接报价格。

**Expected answer points:**

- 客户核心诉求是漆面保护。
- 隐形车衣可用于降低鸟粪虫尸、酸雨水垢、风沙粉尘、高速石子、剐蹭等影响。
- 推荐 1 个主推方案和 1 个升级/备选方案。

## 2. 春分套餐

**Query:** 春分套餐有什么特点？

**Expected behavior:** 命中 `ymyy-solar-chunfen-k7-c15`。

**Expected answer points:**

- 春分套餐是 K7+C15。
- 适用于对健康、环保、隔绝紫外线及隐私性等要求较高的车主。
- 前挡 K7、侧/后挡 C15。
- 返回来源页：有膜有漾服务手册 p.18。

## 3. 贴完能不能洗车

**Query:** 贴完车衣明天能不能洗车？

**Expected behavior:** 命中售后保养规则。

**Expected answer points:**

- 施工后三天内注意保护。
- 车衣与改色施工后三天内不要高速行驶，时速控制在 60 码以内。
- 改色膜三天回店复检，三天内不能洗车。
- 如果客户问的是车衣洗车，建议按门店施工交付提醒执行，不擅自承诺。
- 来源页：有膜有漾服务手册 p.30。

## 4. YM-60 质保

**Query:** YM-60 质保几年？

**Expected behavior:** 命中 `ymyy-ppf-ym60`。

**Expected answer points:**

- YM-60 系列车衣质保期为 3 年。
- 来源页：有膜有漾服务手册 p.8。

## 5. 现在多少钱

**Query:** 现在多少钱？

**Expected behavior:** 命中价格政策边界。

**Expected answer points:**

- 知识库不包含实时价格、活动、库存和施工排期。
- 以门店最新报价和政策为准。
- 可以建议客户提供车型和需求，销售再核准方案。
