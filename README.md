# 有膜有漾 Hermes Sales Agent Profile

This repository contains the Hermes profile, sales skills, vehicle-wrap preview skill, color assets, and knowledge base package for the 有膜有漾 internal sales agent.

## Server Download

The ready-to-upload package is:

```text
build/ymyy-hermes-profile.tar.gz
```

On the server:

```bash
git clone git@github.com:coyafky/hermes-cloud-deployment.git
cd hermes-cloud-deployment
mkdir -p ~/.hermes
tar -xzf build/ymyy-hermes-profile.tar.gz -C ~/
```

The archive expands into:

```text
~/.hermes/profiles/ymyy-sales-agent/
~/.hermes/skills/
~/.hermes/knowledge-base/ymyy-sales-agent/
```

The package includes `ark-seedream-car-preview`, which generates vehicle wrap previews from:

```text
customer vehicle image + preview color-card image + Xinghu gpt-image-2
```

The skill includes the color asset library and preview swatch images under:

```text
~/.hermes/skills/ark-seedream-car-preview/references/color_assets.json
~/.hermes/skills/ark-seedream-car-preview/assets/previews/
```

## Rebuild Package

After editing profile, skills, or knowledge base files:

```bash
bash scripts/package_ymyy_hermes_profile.sh
python3 scripts/validate_ymyy_kb.py
```

Then commit the updated source files and `build/ymyy-hermes-profile.tar.gz`.

## Main Assets

- `hermes-profile/`: SOUL and MEMORY for the sales agent.
- `skills/`: reusable sales workflows and the vehicle-wrap preview generation skill.
- `knowledge-base/ymyy-sales-agent/`: structured service manual knowledge.
- `docs/upload-ymyy-profile-to-server.md`: deployment notes.
