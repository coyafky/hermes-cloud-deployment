---
name: write-sales-followup
description: Use when sales needs a concise WeChat, Feishu, or SMS follow-up message for film product recommendation, quote follow-up, aftercare reminder, or revisit invitation.
---

# Write Sales Follow-Up

## Overview

Use this skill to write short, natural follow-up messages that 有膜有漾 sales can send directly to customers.

## Triggers

Use this skill when the user asks:

- 帮我写跟进话术
- 给客户发什么
- 客户看完套餐后怎么追
- 贴完后注意事项怎么发
- 客户嫌贵后怎么跟进

## Required Inputs

Use any provided context:

- 客户姓名 or 称呼
- 车型
- 客户诉求
- 推荐产品 or 套餐
- 当前阶段：首次咨询、看样膜后、报价后、未回复、施工后提醒

If key context is missing, still produce a generic version and mark placeholders with brackets.

## Workflow

1. Identify the message purpose.
2. Keep it 80-150 Chinese characters unless the user asks for a longer message.
3. Mention one clear customer benefit.
4. Include one low-pressure next step.
5. Avoid hard-selling, fake urgency, invented discounts, and unsupported promises.

## Templates

### Product Recommendation Follow-Up

```markdown
{称呼}，刚才按您说的 {诉求}，我建议先看 {产品/套餐}。它比较适合 {原因}，重点是 {核心价值}。您方便的话，我可以把样膜和对应案例发您看一下，再按您的车型确认具体方案。
```

### Quote Follow-Up

```markdown
{称呼}，您刚才看的 {产品/套餐} 我这边可以先帮您保留方案思路。价格和活动我需要按门店当天政策再确认，避免给您说错。您方便发一下车型和主要需求吗？我帮您核一版更准确的。
```

### Price Objection Follow-Up

```markdown
{称呼}，理解您会对比价格。贴膜主要还是看材料、施工和后续保障是否匹配您的车。我们可以不直接上最高配，先按您的预算做一版合适方案，再看有没有必要升级。
```

### Aftercare Reminder

```markdown
{称呼}，提醒您一下：车衣/改色施工后三天内不要高速行驶，时速尽量控制在 60 码以内；改色膜三天内不要洗车，并按约定回店复检。若雷达有报警或异响，随时联系我们回店处理。
```

## Guardrails

- Do not mention a specific discount unless the user supplied it.
- Do not claim inventory or appointment availability unless supplied.
- For warranty, include the product name and source page if available.
