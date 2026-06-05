# Modular Vehicle Wrap Preview Skill

## Goal

Keep the car-wrap business rules stable while making image API channels replaceable.

The skill now separates:

- asset lookup
- reference image normalization
- request validation
- prompt construction
- provider failover
- output saving

`scripts/gen.py` is only a CLI adapter.

## Provider Failover

Configure multiple OpenAI-compatible channels:

```bash
WRAP_PROVIDER_CHAIN=4sapi_primary,apiyi_primary,xinghu_third,relay_backup
WRAP_PROVIDER_4SAPI_PRIMARY_BASE_URL=https://4sapi.com/v1
WRAP_PROVIDER_4SAPI_PRIMARY_API_KEY=...
WRAP_PROVIDER_4SAPI_PRIMARY_MODEL=gpt-image-2
WRAP_PROVIDER_APIYI_PRIMARY_BASE_URL=https://api.apiyi.com/v1
WRAP_PROVIDER_APIYI_PRIMARY_API_KEY=...
WRAP_PROVIDER_APIYI_PRIMARY_MODEL=gpt-image-2-all
WRAP_PROVIDER_XINGHU_THIRD_BASE_URL=https://xinghuapi.com/v1
WRAP_PROVIDER_XINGHU_THIRD_API_KEY=...
WRAP_PROVIDER_XINGHU_THIRD_MODEL=gpt-image-2
WRAP_PROVIDER_XINGHU_THIRD_REQUEST_STYLE=refs_array
WRAP_PROVIDER_XINGHU_THIRD_WATERMARK=true
WRAP_PROVIDER_XINGHU_THIRD_RESPONSE_FORMAT=url
WRAP_PROVIDER_RELAY_BACKUP_BASE_URL=https://backup.example.com/v1
WRAP_PROVIDER_RELAY_BACKUP_API_KEY=...
WRAP_PROVIDER_RELAY_BACKUP_MODEL=gpt-image-2
```

The router tries providers in order. If one provider fails, it records the failure
and tries the next provider. The wrap-preview service only receives the successful
provider result.

Use `response-format=b64_json` by default for customer delivery flows. Some relays
return protected temporary URLs that can generate successfully but fail during
download with HTTP 403.
