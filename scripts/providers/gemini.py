#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Gemini 3 Pro Image provider for paper-to-image.

Supports txt2img and img2img (editing). Resolution: 1K / 2K / 4K.

Usage (via dispatcher):
    python scripts/generate.py --prompt "..." --filename output/slug.png

Direct usage:
    uv run scripts/providers/gemini.py --prompt "..." --filename output/slug.png \\
        [--resolution 1K|2K|4K] [--input-image path/to/ref.png] [--api-key KEY]
"""

import argparse
import os
import sys
from pathlib import Path


def get_api_key(provided: str | None) -> str | None:
    if provided:
        return provided
    return os.environ.get("GEMINI_API_KEY")


def map_resolution(res: str) -> str:
    """Map 1K/2K/4K to the API image_size string."""
    return {"1K": "1K", "2K": "2K", "4K": "4K"}.get(res.upper(), "1K")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate images with Gemini 3 Pro Image (paper-to-image)"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt or pipeline_configuration JSON")
    parser.add_argument("--filename", "-f", required=True, help="Output PNG path (e.g. output/2026-01-01-draft.png)")
    parser.add_argument("--input-image", "-i", help="Optional input image path for img2img editing")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K")
    parser.add_argument("--model", "-m", default="gemini-3-pro-image-preview", help="Gemini model ID")
    parser.add_argument("--api-key", "-k", help="Gemini API key (overrides GEMINI_API_KEY env var)")
    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No Gemini API key found.", file=sys.stderr)
        print("  Set GEMINI_API_KEY in your environment, or pass --api-key.", file=sys.stderr)
        print("  Get a key at: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)

    from google import genai
    from google.genai import types
    from PIL import Image as PILImage

    client = genai.Client(api_key=api_key)

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_image = None
    output_resolution = args.resolution

    if args.input_image:
        try:
            input_image = PILImage.open(args.input_image)
            print(f"Loaded input image: {args.input_image}")
            if args.resolution == "1K":
                width, height = input_image.size
                max_dim = max(width, height)
                if max_dim >= 3000:
                    output_resolution = "4K"
                elif max_dim >= 1500:
                    output_resolution = "2K"
                print(f"Auto-detected resolution: {output_resolution} (input {width}x{height})")
        except Exception as e:
            print(f"Error loading input image: {e}", file=sys.stderr)
            sys.exit(1)

    if input_image:
        contents = [input_image, args.prompt]
        print(f"Editing image at {output_resolution}...")
    else:
        contents = args.prompt
        print(f"Generating image at {output_resolution}...")

    try:
        response = client.models.generate_content(
            model=args.model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(image_size=output_resolution),
            ),
        )
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)

    saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            import base64
            image_data = base64.b64decode(part.inline_data.data)
            output_path.write_bytes(image_data)
            print(f"\nImage saved: {output_path.resolve()}")
            saved = True
            break

    if not saved:
        text_parts = [
            p.text for p in response.candidates[0].content.parts if p.text
        ]
        print("No image returned by the API.", file=sys.stderr)
        if text_parts:
            print("Model response:", " ".join(text_parts), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
