#!/usr/bin/env python3
"""
Unified image generation dispatcher for paper-to-image.

Reads provider and model from config.json (written by scripts/setup.py)
and delegates to the appropriate provider script in scripts/providers/.

Usage:
    python scripts/generate.py --prompt "$(cat prompt.json)" \\
        --filename output/YYYY-MM-DD-HH-MM-SS-slug.png \\
        [--resolution 1K|2K|4K] \\
        [--input-image path/to/ref.png] \\
        [--provider gemini|fal] \\
        [--model <model-id>] \\
        [--api-key <key>]

Flags:
    --provider   Override the provider in config.json for a single run.
    --model      Override the model in config.json for a single run.
    --api-key    Pass the API key directly (takes priority over env var).
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config.json"
PROVIDERS_DIR = Path(__file__).parent / "providers"

SUPPORTED_PROVIDERS = ["gemini", "fal"]


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"provider": "gemini", "model": "gemini-3-pro-image-preview", "env_var": "GEMINI_API_KEY"}


def main() -> None:
    # ── pre-parse only the flags we need to dispatch ─────────────────────────
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--provider")
    pre.add_argument("--model")
    known, remaining = pre.parse_known_args()

    config = load_config()

    if not CONFIG_PATH.exists():
        print(
            "⚠  config.json not found — using default provider (Gemini).\n"
            "   Run `python scripts/setup.py` to configure your preferred provider.",
            file=sys.stderr,
        )

    provider = known.provider or config.get("provider", "gemini")
    model = known.model or config.get("model")

    if provider not in SUPPORTED_PROVIDERS:
        print(
            f"Error: unknown provider '{provider}'. "
            f"Supported: {', '.join(SUPPORTED_PROVIDERS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    script = PROVIDERS_DIR / f"{provider}.py"
    if not script.exists():
        print(f"Error: provider script not found at {script}", file=sys.stderr)
        sys.exit(1)

    # ── build forwarded args ──────────────────────────────────────────────────
    forward = list(remaining)

    # inject --model from config if not already in args
    if model and "--model" not in forward:
        forward = ["--model", model] + forward

    cmd = ["uv", "run", str(script)] + forward
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
