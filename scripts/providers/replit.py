#!/usr/bin/env python3
"""
Replit platform adapter for paper-to-image.

Replit does not provide its own image generation API. This script:
  1. Reads the underlying provider (gemini or fal) from config.json.
  2. Reads the API key from Replit Secrets (same env vars: GEMINI_API_KEY or FAL_KEY).
  3. Delegates to the appropriate provider script.

Run this from a Replit Repl after setting your API key in:
  Tools → Secrets → Add new secret

Usage (via dispatcher):
    python scripts/generate.py --prompt "..." --filename output/slug.png

Direct usage (inside a Replit Repl):
    python scripts/providers/replit.py --prompt "..." --filename output/slug.png
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = ROOT / "config.json"
PROVIDERS_DIR = Path(__file__).parent


def main() -> None:
    config = {}
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())

    provider = config.get("provider", "gemini")
    if provider == "replit":
        # Shouldn't happen — setup.py always resolves replit to gemini/fal
        provider = "gemini"

    script = PROVIDERS_DIR / f"{provider}.py"
    if not script.exists():
        print(
            f"Error: no provider script for '{provider}' at {script}",
            file=sys.stderr,
        )
        print(
            "Run `python scripts/setup.py` to configure your provider.",
            file=sys.stderr,
        )
        sys.exit(1)

    env_var = config.get("env_var")
    if env_var:
        import os
        val = os.environ.get(env_var, "")
        if not val:
            print(
                f"⚠  {env_var} is not set.\n"
                f"   On Replit: go to Tools → Secrets and add {env_var}.\n"
                f"   Locally: export {env_var}=<your-key>",
                file=sys.stderr,
            )
            sys.exit(1)

    # Forward all args except argv[0]
    forward = sys.argv[1:]
    model = config.get("model")
    if model and "--model" not in forward:
        forward = ["--model", model] + forward

    result = subprocess.run(["uv", "run", str(script)] + forward)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
