# 有膜有漾 Sales Agent 实施说明

## Implemented Assets

- Hermes profile:
  - `hermes-profile/SOUL.md`
  - `hermes-profile/MEMORY.md`
- Skills:
  - `skills/ask-with-mom-test/SKILL.md`
  - `skills/diagnose-with-spin-selling/SKILL.md`
  - `skills/answer-customer-faq-transparently/SKILL.md`
  - `skills/negotiate-with-tactical-empathy/SKILL.md`
  - `skills/strengthen-sales-wording-with-influence/SKILL.md`
  - `skills/recommend-film-product/SKILL.md`
  - `skills/handle-film-objections/SKILL.md`
  - `skills/write-sales-followup/SKILL.md`
- Knowledge base:
  - `knowledge-base/ymyy-sales-agent/ymyy-service-manual.jsonl`
  - `knowledge-base/ymyy-sales-agent/README.md`
  - `knowledge-base/ymyy-sales-agent/source-audit.md`
  - `knowledge-base/ymyy-sales-agent/queries.md`

## Hermes/Flying Book Bot Wiring

1. Load `hermes-profile/SOUL.md` as the agent role and behavior profile.
2. Load `hermes-profile/MEMORY.md` as persistent business memory.
3. Register the eight folders under `skills/` as callable workflows.
4. Index `knowledge-base/ymyy-sales-agent/ymyy-service-manual.jsonl` into the RAG store.
5. Configure retrieval responses to include `source` and `source_page` for parameter and aftercare answers.

## Retrieval Defaults

- `top_k`: 5
- Prefer exact title/id match for product models and package names.
- If a query contains “多少钱”, “活动”, “库存”, “排期”, route to the price-policy entry before product recommendation.
- If a query asks how to ask customers, whether a question is leading, or whether praise counts as demand, route to `ask-with-mom-test`.
- If a query asks about price factors, risks, comparisons, reviews, best fit, or FAQ content, route to `answer-customer-faq-transparently`.
- If a query involves price resistance, hesitation, competitor comparison, family decision, emotional pushback, or low-pressure negotiation, route to `negotiate-with-tactical-empathy`.
- If a query asks to strengthen, polish, make more persuasive, or check whether wording is too pushy, route to `strengthen-sales-wording-with-influence`.
- If a query contains “质保”, “厚度”, “参数”, “阻隔率”, require a cited product entry.
- If a query contains “洗车”, “高速”, “雷达”, “复检”, route to `aftercare_sop`.

## Known Gaps

- p.26-p.29 改色膜图片页未完整录入，当前只提供章节级入口。
- 窗膜参数表中两个同名“紫外线阻隔率”字段保留原文，需要业务人员确认第二个字段是否实际代表其他性能指标。
- 隐形车衣星级来自视觉表格，已按 5 分制转录；建议运营人员二次复核。
