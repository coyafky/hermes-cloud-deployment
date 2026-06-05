# GitHub to Cloud Deployment

本 skill 的正式发布链路以 GitHub 仓库为源头，并优先使用 Hermes profile distribution 更新：

```text
local verified change
  -> push to coyafky/hermes-cloud-deployment
  -> cloud Hermes Agent runs hermes profile update ymyy-sales-agent
  -> distribution refreshes SOUL/profile/skills/knowledge-base
```

不要把本地临时 scp 当作正式发布方式。scp 只适合临时排障；可迭代版本应进入 GitHub，云服务器通过 profile distribution 拉取，方便重复更新、回滚和审计。

## Repository Source

```text
https://github.com/coyafky/hermes-cloud-deployment
skills/ark-seedream-car-preview
```

## Cloud Update Flow

首选方式：

```bash
hermes profile update ymyy-sales-agent
```

首次安装：

```bash
hermes profile install github.com/coyafky/hermes-cloud-deployment --name ymyy-sales-agent --alias
```

Hermes profile distribution 会保留云端本地 `.env`、memory、sessions、logs、auth 等用户数据。

### Fallback: Manual Git Pull

只有在 profile distribution 暂不可用或需要临时排障时，才使用手动 git pull + rsync。

在云服务器中：

```bash
cd ~/hermes-cloud-deployment
git pull --ff-only origin main
```

如果云端还没有 clone：

```bash
git clone https://github.com/coyafky/hermes-cloud-deployment.git ~/hermes-cloud-deployment
```

然后把 repo 中的 skill 同步到 Hermes profile：

```bash
PROFILE_DIR="$HOME/.hermes/profiles/ymyy-sales-agent"
SRC="$HOME/hermes-cloud-deployment/skills/ark-seedream-car-preview"
DST="$PROFILE_DIR/skills/ark-seedream-car-preview"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$PROFILE_DIR/backups"
[ -d "$DST" ] && cp -a "$DST" "$PROFILE_DIR/backups/ark-seedream-car-preview-$STAMP"

mkdir -p "$DST"
rsync -a \
  --exclude '.env' \
  --exclude '.env.local' \
  --exclude '.local.json' \
  --exclude 'tmp/' \
  --exclude 'scripts/tmp/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  "$SRC/" "$DST/"
```

密钥文件必须保留在云端 profile 或 skill 本地目录，不能提交到 GitHub：

```text
$DST/.env
$DST/.env.local
$DST/.local.json
$PROFILE_DIR/.env
$PROFILE_DIR/.env.local
```

## Required Provider Config

云端至少需要一个真实 provider key。建议使用 `.env.local`：

```bash
WRAP_PROVIDER_CHAIN=4sapi_primary,apiyi_primary,xinghu_third,relay_backup

WRAP_PROVIDER_4SAPI_PRIMARY_BASE_URL=https://4sapi.com/v1
WRAP_PROVIDER_4SAPI_PRIMARY_API_KEY=...
WRAP_PROVIDER_4SAPI_PRIMARY_MODEL=gpt-image-2
WRAP_PROVIDER_4SAPI_PRIMARY_AUTH_SCHEME=bearer

WRAP_PROVIDER_APIYI_PRIMARY_BASE_URL=https://api.apiyi.com/v1
WRAP_PROVIDER_APIYI_PRIMARY_API_KEY=...
WRAP_PROVIDER_APIYI_PRIMARY_MODEL=gpt-image-2-all
WRAP_PROVIDER_APIYI_PRIMARY_AUTH_SCHEME=bearer

WRAP_PROVIDER_XINGHU_THIRD_BASE_URL=https://xinghuapi.com/v1
WRAP_PROVIDER_XINGHU_THIRD_API_KEY=...
WRAP_PROVIDER_XINGHU_THIRD_MODEL=gpt-image-2
WRAP_PROVIDER_XINGHU_THIRD_AUTH_SCHEME=bearer
WRAP_PROVIDER_XINGHU_THIRD_REQUEST_STYLE=refs_array
WRAP_PROVIDER_XINGHU_THIRD_WATERMARK=true
WRAP_PROVIDER_XINGHU_THIRD_RESPONSE_FORMAT=url
```

旧字段仍可被兼容读取：

```text
APIYI_API_KEY
4S_API_KEY
FOURS_API_KEY
apiyi_api_key in .local.json
```

## Verification

在云端 profile skill 目录运行：

```bash
cd "$PROFILE_DIR/skills/ark-seedream-car-preview"
python3 -m unittest discover -s tests -v
```

使用飞书缓存图片做 dry-run：

```bash
CAR_IMAGE="$(find "$PROFILE_DIR/cache/images" -maxdepth 1 -type f | head -n 1)"

python3 scripts/gen.py \
  --vehicle-ref "$CAR_IMAGE" \
  --asset-id B-121 \
  --size auto \
  --quality high \
  --response-format b64_json \
  --dry-run
```

验证飞书发送命令结构，不真实发送：

```bash
python3 scripts/gen_and_send.py \
  --channel feishu \
  --target feishu:dry-run-target \
  --vehicle-ref "$CAR_IMAGE" \
  --asset-id B-121 \
  --size auto \
  --quality high \
  --response-format b64_json \
  --dry-run-send \
  --skip-status-message
```

真实发送时必须使用明确 target，不要使用 `origin`：

```bash
python3 scripts/gen_and_send.py \
  --channel feishu \
  --target 'feishu:<real-open-id-or-chat-id>' \
  --vehicle-ref "$CAR_IMAGE" \
  --asset-id B-121 \
  --response-format b64_json
```

## Success Criteria

- unit tests pass
- dry-run refs include both customer vehicle image and preview swatch image
- providers show at least one `has_api_key: true`; for full production failover, 4sapi, APIYi, and Xinghu should all show `has_api_key: true`
- `gen_and_send.py --dry-run-send` contains `openclaw message send --channel feishu --media <generated image path>`
- no real secret appears in GitHub-tracked files
