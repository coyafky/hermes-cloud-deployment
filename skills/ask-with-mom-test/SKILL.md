---
name: ask-with-mom-test
description: Use The Mom Test principles to ask non-leading C-end car-film sales questions, detect weak signals, and turn vague interest into concrete next steps.
source_book: The Mom Test, Rob Fitzpatrick
---

# Ask With The Mom Test

## Overview

Use this skill before recommending 有膜有漾车衣、窗膜、改色膜 when the customer need is still vague. The goal is to get truthful customer data without leading the customer toward praise, fake interest, or future hypotheticals.

The operating rule:

- Ask about the customer's life, not your product.
- Ask about past facts, not future guesses.
- Ask about specifics, not opinions.
- Treat compliments as weak signals until the customer gives time, reputation, money, or a concrete next step.

## Triggers

Use this skill when the user asks:

- 怎么问客户真实需求
- 客户说挺好但不下单怎么办
- 这个问题会不会太诱导
- 帮我把销售问题改得更自然
- 客户只是随便了解一下怎么聊
- 客户说如果便宜点就会贴，这算有效需求吗
- 帮我设计几个不引导客户的问题

## Do Not Use When

- The customer already gave a clear product request and only needs parameters or warranty lookup.
- The conversation has moved to a concrete product comparison; use `recommend-film-product`.
- The customer is objecting to price, warranty, quality, or aftercare; use `handle-film-objections`.
- The customer is bargaining, hesitating, comparing competitors, or resisting emotionally; use `negotiate-with-tactical-empathy`.
- The sales person needs a final customer message; use `write-sales-followup`.

## Workflow

1. Identify the current signal.
   - Compliment: “挺好”“很专业”“我喜欢”.
   - Fluff: “以后可能会”“有机会再说”“如果便宜点”.
   - Opinion: “你觉得好不好”“你会不会推荐”.
   - Fact: actual vehicle, past problem, prior solution, real budget, specific timeline.
   - Commitment: model confirmation, store visit, sample review, introduction, deposit, appointment.
2. If the question is leading, rewrite it.
   - Bad: “您是不是也觉得车衣很有必要？”
   - Better: “您之前有没有遇到过车漆剐蹭、补漆或太阳纹？当时怎么处理的？”
3. Pull future claims back to past behavior.
   - If customer says “以后会贴”, ask what happened last time they considered film, what they compared, and what stopped them.
4. Deflect compliments.
   - Thank briefly, then ask for facts: “谢谢认可。想更准确推荐，我想了解一下您之前遇到过哪些用车问题？”
5. Seek commitment or advancement.
   - Do not treat praise as progress.
   - Ask for a small next step: confirm vehicle, visit store, view sample, compare packages, schedule inspection, or introduce another decision-maker.
6. Hand off to the next skill.
   - If a real pain is found, use `diagnose-with-spin-selling`.
   - If the need is clear, use `recommend-film-product`.
   - If resistance appears, use `handle-film-objections` or `negotiate-with-tactical-empathy`.

## Output Template

```markdown
判断：这句话属于 {赞美/空泛假设/意见/事实/承诺}，当前还不能算强需求。

原因：{一句话说明为什么这个信号强或弱}

建议这样问：
1. {不诱导、问过去事实的问题}
2. {追问具体场景/已有解决方案的问题}
3. {请求小承诺或下一步的问题}

下一步：如果客户回答 {具体信号}，再调用 `{next_skill}`。
```

## Good Question Rules

- Ask about what already happened.
- Ask what they already tried.
- Ask what it cost in time, money, comfort, or risk.
- Ask who else is involved in the decision.
- Ask for a specific next step instead of accepting vague interest.

## Bad Question Patterns

- “您觉得我们这个产品好不好？”
- “如果价格合适您会买吗？”
- “您是不是也担心车漆被刮？”
- “您会推荐朋友来贴吗？”
- “我们这个套餐很划算吧？”

## Guardrails

- Do not trick customers. The goal is truthful discovery, not manipulation.
- Do not argue with compliments or vague answers; convert them into concrete facts.
- Do not ask a long questionnaire. Use 2-3 questions, then listen.
- Do not mention price, discount, activity, inventory, or construction schedule unless store policy confirms it.
- Do not treat “以后会买” as progress unless it is paired with a concrete commitment.

## Connects To

- `diagnose-with-spin-selling`: use after Mom Test questions surface a real pain or goal.
- `recommend-film-product`: use after the customer has a clear need and vehicle context.
- `handle-film-objections`: use when vague interest turns into price or risk objection.
- `negotiate-with-tactical-empathy`: use when vague interest turns into bargaining, hesitation, competitor comparison, or decision delay.
- `write-sales-followup`: use to turn the discovered facts and next step into a customer-facing message.
