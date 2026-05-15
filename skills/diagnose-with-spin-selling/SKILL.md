---
name: diagnose-with-spin-selling
description: Use SPIN Selling to diagnose a C-end car-film customer's real needs before recommending paint protection film, window film, or color-change film.
source_book: SPIN Selling, Neil Rackham
---

# Diagnose With SPIN Selling

## Overview

Use this skill when 有膜有漾 sales needs to understand a customer's buying motive before recommending a film product. The goal is to move from surface interest to a clear customer-owned need, then connect that need to the right product from the 有膜有漾 knowledge base.

SPIN is not a script. It is a questioning sequence:

- Situation: understand the current context.
- Problem: uncover dissatisfaction or risk.
- Implication: help the customer see the consequence of leaving the problem unsolved.
- Need-payoff: help the customer state the value of solving it.

## Triggers

Use this skill when the user asks:

- 客户适合贴什么膜
- 怎么问客户需求
- 客户说想了解一下，怎么聊
- 客户不知道选车衣还是窗膜
- 怎么把客户需求挖深
- 怎么避免一上来就报价

## Do Not Use When

- The customer only needs a factual parameter lookup, such as "YM-60 质保几年".
- The customer is already in aftercare or complaint handling; use aftercare/objection skills first.
- The user asks for price, inventory, campaign, or schedule; route to store policy boundaries.

## Workflow

1. Identify the sales stage.
   - First inquiry: use Situation and Problem questions.
   - Comparing options: use Problem and Implication questions.
   - Ready to decide: use Need-payoff questions and recommend the next step.
2. Ask no more than 2-3 questions at a time.
   - Too many questions feels like interrogation.
   - Prefer natural WeChat-style wording.
3. Keep Situation questions light.
   - Ask only what is needed for recommendation: vehicle, age, parking, driving, family use, budget.
4. Use Problem questions to locate the real buying motive.
   - Paint risk: scratches, stones, bird droppings, acid rain, new-car paint.
   - Cabin comfort: heat, glare, privacy, UV concern, family passengers.
   - Appearance: color change, style, resale concerns.
5. Use Implication questions carefully.
   - Do not scare the customer.
   - Connect consequences to their context, such as repaint cost, daily discomfort, family concerns, or repeat maintenance.
6. Use Need-payoff questions before recommending.
   - Let the customer confirm what improvement matters.
   - Then call `recommend-film-product` with the diagnosed need.
7. Produce a recommendation brief.
   - Customer profile
   - Main pain
   - Confirmed value
   - Recommended category
   - Questions still missing

## SPIN Question Bank For Car Film

See `references/car-film-spin-question-bank.md` for ready-to-use questions by product category.

## Output Template

```markdown
初步判断：客户现在属于 {阶段}，核心诉求更偏向 {漆面保护/隔热隐私/外观改色/还不明确}。

建议先这样问：
1. {Situation 或 Problem 问题}
2. {Problem 或 Implication 问题}
3. {Need-payoff 问题}

如果客户回答 {可能回答}，下一步可以推荐 {产品方向}，并调用 `recommend-film-product` 查具体产品。

注意：暂时不要报价；价格、活动和排期以门店最新政策为准。
```

## Guardrails

- Do not use SPIN to manipulate fear. Make risks concrete but calm.
- Do not turn every conversation into a long questionnaire.
- Do not recommend a product before at least one meaningful Problem or Need-payoff signal is known.
- Do not invent product claims; use the 有膜有漾 knowledge base for specs and warranty.
- Do not hard-close. In a C-end car-film context, the next commitment is usually: confirm model, view sample, compare package, visit store, or schedule inspection.

## Connects To

- `recommend-film-product`: use after diagnosis to choose car film category or package.
- `handle-film-objections`: use when the customer pushes back on price, necessity, quality, or warranty.
- `negotiate-with-tactical-empathy`: use when the customer starts bargaining, hesitating, comparing competitors, or delaying through a decision process.
- `write-sales-followup`: use after diagnosis to send a concise follow-up message.
