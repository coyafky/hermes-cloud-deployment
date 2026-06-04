# 有膜有漾 Hermes Sales Agent Distribution

This repository is a Hermes profile distribution for `ymyy-sales-agent`.

It packages the sales agent SOUL, profile metadata, knowledge assets, sales skills, and the `ark-seedream-car-preview` vehicle wrap preview skill. Cloud servers should install or update this repository as a Hermes profile distribution instead of manually copying files.

## Install

On a cloud server:

```bash
hermes profile install github.com/coyafky/hermes-cloud-deployment --name ymyy-sales-agent --alias
```

If the profile already exists and was created manually, back it up first:

```bash
cp -a ~/.hermes/profiles/ymyy-sales-agent ~/.hermes/profiles/ymyy-sales-agent.backup-$(date +%Y%m%d-%H%M%S)
```

## Update

After changes are pushed to GitHub:

```bash
hermes profile update ymyy-sales-agent
```

Hermes preserves user-owned data during updates, including `.env`, memories, sessions, logs, and auth files. That is the reason this repository now uses profile distributions instead of a manual tarball or repeated `rsync` workflow.

## Required Local Secrets

Do not commit API keys to this repository. Configure provider keys on each machine in the installed profile's `.env` or `.env.local`.

Recommended image provider configuration:

```bash
WRAP_PROVIDER_CHAIN=4sapi_primary,apiyi_primary,relay_backup

WRAP_PROVIDER_4SAPI_PRIMARY_BASE_URL=https://4sapi.com/v1
WRAP_PROVIDER_4SAPI_PRIMARY_API_KEY=replace-with-local-key
WRAP_PROVIDER_4SAPI_PRIMARY_MODEL=gpt-image-2
WRAP_PROVIDER_4SAPI_PRIMARY_AUTH_SCHEME=bearer

WRAP_PROVIDER_APIYI_PRIMARY_BASE_URL=https://api.apiyi.com/v1
WRAP_PROVIDER_APIYI_PRIMARY_API_KEY=replace-with-local-key
WRAP_PROVIDER_APIYI_PRIMARY_MODEL=gpt-image-2-all
WRAP_PROVIDER_APIYI_PRIMARY_AUTH_SCHEME=bearer
```

Legacy local fields are still accepted by the car preview skill:

```text
APIYI_API_KEY
4S_API_KEY
FOURS_API_KEY
apiyi_api_key in .local.json
```

## Vehicle Wrap Preview

The current image generation workflow is:

```text
customer vehicle image
  + color asset preview swatch image
  + structured prompt
  + OpenAI-compatible provider chain
  -> realistic vehicle wrap preview
```

The key skill is:

```text
skills/ark-seedream-car-preview
```

Run local verification inside that skill:

```bash
cd skills/ark-seedream-car-preview
python3 -m unittest discover -s tests -v
```

Dry-run with a Feishu cached image:

```bash
PROFILE_DIR="$HOME/.hermes/profiles/ymyy-sales-agent"
CAR_IMAGE="$(find "$PROFILE_DIR/cache/images" -maxdepth 1 -type f | head -n 1)"

python3 scripts/gen.py \
  --vehicle-ref "$CAR_IMAGE" \
  --asset-id B-121 \
  --size auto \
  --quality high \
  --response-format b64_json \
  --dry-run
```

Check Feishu delivery command shape without sending:

```bash
python3 scripts/gen_and_send.py \
  --channel feishu \
  --target feishu:dry-run-target \
  --vehicle-ref "$CAR_IMAGE" \
  --asset-id B-121 \
  --response-format b64_json \
  --dry-run-send \
  --skip-status-message
```

For real script-based delivery, use an explicit Feishu target. Do not use `origin` as a send target.

## Distribution Files

- `distribution.yaml`: Hermes distribution manifest.
- `SOUL.md`: agent behavior and routing rules.
- `profile.yaml`: profile metadata and sales-generation settings.
- `skills/`: bundled sales workflows and vehicle wrap preview skill.
- `knowledge-base/`: structured sales knowledge.
- `docs/`: implementation and deployment notes.

## Never Commit

These files must stay local to each server or developer machine:

```text
.env
.env.local
.local.json
skills/*/.env
skills/*/.env.local
skills/*/.local.json
auth.json
sessions/
logs/
memories/
```
