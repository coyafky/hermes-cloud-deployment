---
name: answer-customer-faq-transparently
description: Use They Ask, You Answer principles to answer C-end car-film customer questions about price, risks, comparisons, reviews, and best-fit choices with transparency and clear boundaries.
source_book: They Ask, You Answer, Marcus Sheridan
---

# Answer Customer FAQ Transparently

## Overview

Use this skill when 有膜有漾 sales needs to answer the hard questions customers actually care about: price, risk, comparison, warranty, alternatives, best choice, and whether a product is a fit. The goal is to build trust by educating clearly, not hiding uncomfortable topics.

This skill adapts They Ask, You Answer and The Big 5 to C-end car-film sales:

- Cost and price
- Problems and risks
- Versus and comparisons
- Reviews and social proof
- Best-in-class and best-fit choices

## Triggers

Use this skill when the user asks:

- 客户问为什么这么贵怎么答
- 客户问车衣有没有必要
- 客户问贴膜会不会伤车
- 客户问不同套餐怎么选
- 帮我写一段透明的价格解释
- 客户问我们和别家有什么区别
- 帮我整理销售 FAQ
- 客户问基础款和高阶款差在哪里
- 客户问有没有缺点、风险、售后边界

## Do Not Use When

- The user only needs a factual product spec lookup; query the product knowledge base first.
- The customer need is still vague; use `ask-with-mom-test` or `diagnose-with-spin-selling` first.
- The customer asks for a specific real-time price, promotion, inventory, or schedule; explain the boundary and route to store confirmation.
- A quality dispute requires inspection; do not assign fault remotely.

## Workflow

1. Classify the question into The Big 5.
   - Cost: price, budget, why expensive, why cheap options differ.
   - Problems: risks, defects, aftercare, construction concerns.
   - Comparison: product A vs product B, us vs others, car film categories.
   - Reviews: cases, word of mouth, real feedback, proof.
   - Best fit: who should choose what, who should not choose what.
2. Answer directly first.
   - Do not dodge the uncomfortable part.
   - Start with a plain-language answer before explaining details.
3. Explain the decision factors.
   - Use customer context: vehicle, usage, parking, family passengers, budget, risk tolerance.
   - Use verified product knowledge for specs, warranty, and aftercare.
4. Give fit and non-fit guidance.
   - Say who the option is suitable for.
   - Say when it may be unnecessary or not the best first choice.
5. State boundaries.
   - Prices, campaigns, inventory, and schedules require store confirmation.
   - Warranty and specs must cite source pages when available.
6. End with the next useful step.
   - Confirm model, compare two packages, view samples, visit store, or receive a transparent quote.

## The Big 5 For Car Film

See `references/big-5-car-film-faq.md` for ready-to-use FAQ prompts.

## Output Template

```markdown
透明回答：
{先直接回答客户最关心的问题，不绕开}

主要影响因素：
1. {因素1}
2. {因素2}
3. {因素3}

适合谁：
{适合的客户/车型/场景}

不一定适合谁：
{不适合或没必要升级的场景}

下一步：
{确认车型/看样膜/对比套餐/到店检查/门店确认报价}

边界：
价格、活动、库存和施工排期以门店最新确认为准；参数和质保以知识库来源页为准。
```

## Guardrails

- Do not hide price concerns; explain what drives price, but do not invent a quote.
- Do not attack competitors. Compare materials, construction, warranty, aftercare, and fit.
- Do not claim all customers need the highest tier.
- Do not invent reviews, cases, ratings, or customer feedback.
- Do not answer warranty, thickness, or aftercare from memory when the knowledge base has a source page.
- Do not confuse transparency with overpromising; honest limits build trust.

## Connects To

- `ask-with-mom-test`: use before this skill when the customer signal may be vague or performative.
- `diagnose-with-spin-selling`: use to deepen the need before answering best-fit questions.
- `recommend-film-product`: use after education when the customer needs a concrete package.
- `handle-film-objections`: use when the FAQ becomes a direct objection.
- `negotiate-with-tactical-empathy`: use when the FAQ turns into bargaining, hesitation, competitor comparison, or emotional resistance.
- `write-sales-followup`: use to turn the transparent answer into a customer-facing WeChat or Feishu message.
