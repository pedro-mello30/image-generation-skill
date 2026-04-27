#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fal-client>=0.10.0",
#     "pillow>=10.0.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
fal.ai provider for paper-to-image.

Supports txt2img and img2img (via image_url or uploaded input).
Models: fal-ai/imagen4/preview (default), fal-ai/flux-pro, fal-ai/flux/schnell.

Usage (via dispatcher):
    python scripts/generate.py --prompt "..." --filename output/slug.png

Direct usage:
    uv run scripts/providers/fal_ai.py --prompt "..." --filename output/slug.png \\
        [--resolution 1K|2K|4K] [--input-image path/to/ref.png] [--api-key KEY]
        [--model fal-ai/imagen4/preview]
"""

import argparse
import os
import sys
from pathlib import Path

# Resolution → (width, height) for the fal image_size dict
RESOLUTION_MAP = {
    "1K": {"width": 1024, "height": 1024},
    "2K": {"width": 2048, "height": 2048},
    "4K": {"width": 4096, "height": 4096},
}

# Models that support img2img natively via image_url
IMG2IMG_CAPABLE = {
    "fal-ai/flux-pro",
    "fal-ai/flux/dev",
    "fal-ai/imagen4/preview",
}


def get_api_key(provided: str | None) -> str | None:
    if provided:
        return provided
    return os.environ.get("FAL_KEY")


def upload_image(path: str) -> str:
    """Upload a local image to fal storage and return the URL."""
    import fal_client
    url = fal_client.upload_file(path)
    return url


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate images with fal.ai (paper-to-image)"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt or pipeline_configuration JSON")
    parser.add_argument("--filename", "-f", required=True, help="Output PNG path (e.g. output/2026-01-01-draft.png)")
    parser.add_argument("--input-image", "-i", help="Optional input image path for img2img editing")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K")
    parser.add_argument("--model", "-m", default="fal-ai/imagen4/preview", help="fal.ai model ID")
    parser.add_argument("--api-key", "-k", help="fal.ai API key (overrides FAL_KEY env var)")
    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No fal.ai API key found.", file=sys.stderr)
        print("  Set FAL_KEY in your environment, or pass --api-key.", file=sys.stderr)
        print("  Get a key at: https://fal.ai/dashboard/keys", file=sys.stderr)
        sys.exit(1)

    os.environ["FAL_KEY"] = api_key

    import fal_client
    import httpx

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_size = RESOLUTION_MAP.get(args.resolution, RESOLUTION_MAP["1K"])
    model = args.model

    arguments: dict = {
        "prompt": args.prompt,
        "image_size": image_size,
        "num_images": 1,
        "output_format": "png",
    }

    if args.input_image:
        if model not in IMG2IMG_CAPABLE:
            print(
                f"Warning: model '{model}' may not support img2img. "
                "Trying anyway — use fal-ai/flux-pro or fal-ai/imagen4/preview for best results.",
                file=sys.stderr,
            )
        try:
            print(f"Uploading input image: {args.input_image}")
            image_url = upload_image(args.input_image)
            arguments["image_url"] = image_url
            print(f"Editing image at {args.resolution}...")
        except Exception as e:
            print(f"Error uploading input image: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Generating image at {args.resolution} with {model}...")

    try:
        result = fal_client.run(model, arguments=arguments)
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)

    images = result.get("images") or []
    if not images:
        print("No image returned by the API.", file=sys.stderr)
        print(f"Full response: {result}", file=sys.stderr)
        sys.exit(1)

    image_url = images[0].get("url") or images[0].get("image_url")
    if not image_url:
        print("Could not extract image URL from response.", file=sys.stderr)
        sys.exit(1)

    try:
        response = httpx.get(image_url, timeout=120)
        response.raise_for_status()
        output_path.write_bytes(response.content)
        print(f"\nImage saved: {output_path.resolve()}")
    except Exception as e:
        print(f"Error downloading image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
