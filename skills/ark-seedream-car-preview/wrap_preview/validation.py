from __future__ import annotations

from .models import WrapPreviewRequest


def validate_reference_images(request: WrapPreviewRequest) -> None:
    if not request.vehicle_refs:
        raise ValueError("Missing --vehicle-ref. The car-wrap workflow must use the customer's vehicle image as the first reference.")
    if not request.color_refs:
        raise ValueError("Missing preview color-card image. Use --asset-id with an asset that has images.swatch, or pass --color-ref. HEX/Lab-only generation is disabled.")
    if len(request.raw_refs) < 2:
        raise ValueError("The car-wrap workflow requires two image references: customer vehicle image + preview color-card image.")

