#!/usr/bin/env python3
"""
First-run provider setup for paper-to-image.

Run from the repo root:
    python scripts/setup.py

Writes config.json with the selected provider, model, and env-var name.
The actual API key stays in your shell environment — never in config.json.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config.json"

PROVIDERS = {
    "gemini": {
        "label": "Google AI Studio — Gemini 3 Pro Image (default, recommended)",
        "env_var": "GEMINI_API_KEY",
        "key_url": "https://aistudio.google.com/apikey",
        "models": [
            "gemini-3-pro-image-preview",
        ],
        "default_model": "gemini-3-pro-image-preview",
        "resolutions": ["1K", "2K", "4K"],
        "notes": (
            "Best overall quality for paper-style and whiteboard figures. "
            "Supports 1K / 2K / 4K output and img2img editing."
        ),
    },
    "fal": {
        "label": "fal.ai — FLUX Pro, Imagen 4, and more",
        "env_var": "FAL_KEY",
        "key_url": "https://fal.ai/dashboard/keys",
        "models": [
            "fal-ai/imagen4/preview",
            "fal-ai/flux-pro",
            "fal-ai/flux/schnell",
        ],
        "default_model": "fal-ai/imagen4/preview",
        "resolutions": ["1K", "2K", "4K"],
        "notes": (
            "Large model catalogue. Imagen 4 is recommended for scientific figures. "
            "FLUX Schnell is fastest for rapid iteration."
        ),
    },
    "replit": {
        "label": "Replit — run on Replit platform (uses Gemini or fal.ai keys via Replit Secrets)",
        "env_var": None,
        "key_url": "https://replit.com/account",
        "models": [],
        "default_model": None,
        "resolutions": ["1K", "2K", "4K"],
        "notes": (
            "Replit does not provide its own image generation API. "
            "Choosing this option configures the skill to read API keys from Replit Secrets "
            "and lets you pick Gemini or fal.ai as the underlying model provider."
        ),
    },
}


def ask(prompt: str, options: list[str], default: int = 1) -> str:
    while True:
        raw = input(f"{prompt} [default {default}]: ").strip() or str(default)
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        valid = ", ".join(str(i) for i in range(1, len(options) + 1))
        print(f"  Invalid choice. Enter one of: {valid}")


def main() -> None:
    print("\n=== paper-to-image — first-run provider setup ===\n")

    # ── 1. Choose provider ────────────────────────────────────────────────────
    provider_keys = list(PROVIDERS.keys())
    print("Which image generation provider do you want to use?\n")
    for i, key in enumerate(provider_keys, 1):
        p = PROVIDERS[key]
        print(f"  {i}. {p['label']}")
        print(f"     {p['notes']}\n")

    provider = ask("Enter number", provider_keys)
    p = PROVIDERS[provider]
    print(f"\n✓ Provider: {provider}")

    # ── 2. Replit: pick underlying provider ───────────────────────────────────
    if provider == "replit":
        print("\nReplit platform selected.")
        print("You still need an underlying image model. Which one?\n")
        sub_keys = [k for k in provider_keys if k != "replit"]
        for i, key in enumerate(sub_keys, 1):
            s = PROVIDERS[key]
            print(f"  {i}. {s['label']}")
        sub_provider = ask("Enter number", sub_keys)
        p = PROVIDERS[sub_provider]
        print(f"\n✓ Underlying provider: {sub_provider}")
        print(
            f"  Set {p['env_var']} as a Replit Secret at: "
            f"https://replit.com — Tools → Secrets"
        )
        config = {
            "provider": sub_provider,
            "platform": "replit",
            "model": p["default_model"],
            "env_var": p["env_var"],
        }
    else:
        config = {
            "provider": provider,
            "platform": "local",
            "model": p["default_model"],
            "env_var": p["env_var"],
        }

    # ── 3. Choose model ───────────────────────────────────────────────────────
    if p["models"]:
        print(f"\nAvailable models for {config['provider']}:\n")
        for i, m in enumerate(p["models"], 1):
            default_marker = " (default)" if m == p["default_model"] else ""
            print(f"  {i}. {m}{default_marker}")
        model_choice = ask("Enter number", p["models"])
        config["model"] = model_choice
        print(f"\n✓ Model: {config['model']}")

    # ── 4. API key check ──────────────────────────────────────────────────────
    env_var = p["env_var"]
    if env_var:
        env_val = os.environ.get(env_var, "")
        print(f"\nAPI key env var: {env_var}")
        print(f"Get your key at: {p['key_url']}")
        if env_val:
            print(f"✓ {env_var} is already set in this shell.")
        else:
            print(
                f"⚠  {env_var} is NOT set in this shell.\n"
                f"   Add this to your shell profile (e.g. ~/.bashrc or ~/.zshrc):\n"
                f"   export {env_var}=<your-key>\n"
                f"   Never put the key in config.json or any committed file."
            )

    # ── 5. Write config ───────────────────────────────────────────────────────
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n")

    print(f"\n✓ Config written to config.json")
    print(f"  provider : {config['provider']}")
    print(f"  model    : {config.get('model', 'n/a')}")
    print(f"  platform : {config.get('platform', 'local')}")
    print(
        "\nAll set. Re-run `python scripts/setup.py` at any time to switch providers.\n"
    )
    print("To generate your first image:")
    print(
        "  python scripts/generate.py \\\n"
        "    --prompt \"$(cat prompt.json)\" \\\n"
        "    --filename output/$(date +%Y-%m-%d-%H-%M-%S)-draft.png \\\n"
        "    --resolution 1K"
    )
    print()


if __name__ == "__main__":
    main()
