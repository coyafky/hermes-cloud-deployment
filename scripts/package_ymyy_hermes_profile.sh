#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/build/ymyy-hermes-profile"
PROFILE_NAME="ymyy-sales-agent"

rm -rf "${OUT_DIR}"
mkdir -p \
  "${OUT_DIR}/.hermes/profiles/${PROFILE_NAME}" \
  "${OUT_DIR}/.hermes/skills" \
  "${OUT_DIR}/.hermes/knowledge-base/${PROFILE_NAME}"

cp "${ROOT_DIR}/hermes-profile/SOUL.md" "${OUT_DIR}/.hermes/profiles/${PROFILE_NAME}/SOUL.md"
cp "${ROOT_DIR}/hermes-profile/MEMORY.md" "${OUT_DIR}/.hermes/profiles/${PROFILE_NAME}/MEMORY.md"

cp -R "${ROOT_DIR}/skills/recommend-film-product" "${OUT_DIR}/.hermes/skills/"
cp -R "${ROOT_DIR}/skills/handle-film-objections" "${OUT_DIR}/.hermes/skills/"
cp -R "${ROOT_DIR}/skills/write-sales-followup" "${OUT_DIR}/.hermes/skills/"
cp -R "${ROOT_DIR}/skills/diagnose-with-spin-selling" "${OUT_DIR}/.hermes/skills/"
cp -R "${ROOT_DIR}/skills/ask-with-mom-test" "${OUT_DIR}/.hermes/skills/"
cp -R "${ROOT_DIR}/skills/answer-customer-faq-transparently" "${OUT_DIR}/.hermes/skills/"
cp -R "${ROOT_DIR}/skills/negotiate-with-tactical-empathy" "${OUT_DIR}/.hermes/skills/"
cp -R "${ROOT_DIR}/skills/strengthen-sales-wording-with-influence" "${OUT_DIR}/.hermes/skills/"

cp "${ROOT_DIR}/knowledge-base/ymyy-sales-agent/ymyy-service-manual.jsonl" \
  "${OUT_DIR}/.hermes/knowledge-base/${PROFILE_NAME}/ymyy-service-manual.jsonl"
cp "${ROOT_DIR}/knowledge-base/ymyy-sales-agent/README.md" \
  "${OUT_DIR}/.hermes/knowledge-base/${PROFILE_NAME}/README.md"
cp "${ROOT_DIR}/knowledge-base/ymyy-sales-agent/source-audit.md" \
  "${OUT_DIR}/.hermes/knowledge-base/${PROFILE_NAME}/source-audit.md"
cp "${ROOT_DIR}/knowledge-base/ymyy-sales-agent/queries.md" \
  "${OUT_DIR}/.hermes/knowledge-base/${PROFILE_NAME}/queries.md"

cat > "${OUT_DIR}/.hermes/profiles/${PROFILE_NAME}/profile.yaml" <<'YAML'
name: ymyy-sales-agent
display_name: 有膜有漾内部销售助手
description: 面向门店销售、招商人员和客服的有膜有漾销售知识助手
soul: SOUL.md
memory: MEMORY.md
skills:
  - ask-with-mom-test
  - diagnose-with-spin-selling
  - answer-customer-faq-transparently
  - negotiate-with-tactical-empathy
  - strengthen-sales-wording-with-influence
  - recommend-film-product
  - handle-film-objections
  - write-sales-followup
knowledge_base:
  - ../../knowledge-base/ymyy-sales-agent/ymyy-service-manual.jsonl
retrieval:
  top_k: 5
  require_source_page_for:
    - 参数
    - 质保
    - 厚度
    - 阻隔率
    - 售后
guardrails:
  - 不回答实时价格、活动、库存、施工排期，提示以门店最新政策为准。
  - 不承诺手册中没有写明的质保、效果或售后责任。
YAML

cat > "${OUT_DIR}/README.md" <<'MARKDOWN'
# 有膜有漾 Hermes Profile Upload Package

This package is intended to be copied into the server user's `~/.hermes/` directory.

Expected destination:

```text
~/.hermes/profiles/ymyy-sales-agent/
~/.hermes/skills/ask-with-mom-test/
~/.hermes/skills/diagnose-with-spin-selling/
~/.hermes/skills/answer-customer-faq-transparently/
~/.hermes/skills/negotiate-with-tactical-empathy/
~/.hermes/skills/strengthen-sales-wording-with-influence/
~/.hermes/skills/recommend-film-product/
~/.hermes/skills/handle-film-objections/
~/.hermes/skills/write-sales-followup/
~/.hermes/knowledge-base/ymyy-sales-agent/
```

After upload, point the Feishu/Hermes gateway to profile `ymyy-sales-agent`.
MARKDOWN

tar -C "${OUT_DIR}" -czf "${ROOT_DIR}/build/ymyy-hermes-profile.tar.gz" .

echo "Built: ${OUT_DIR}"
echo "Archive: ${ROOT_DIR}/build/ymyy-hermes-profile.tar.gz"
