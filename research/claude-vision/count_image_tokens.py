# /// script
# requires-python = ">=3.14"
# dependencies = ["anthropic", "pillow", "platformdirs"]
# ///
"""Count the image tokens of screenshots with Anthropic's count_tokens endpoint.

For each image path: native size plus the variants from research/claude-vision-tokens.md item 4
(downscaled to 960 and 640 px wide, a centre-half crop), each encoded in memory as PNG and as
JPEG q85. One JSON line per variant, with the patch formula's prediction alongside.

  uv run research/claude-vision/count_image_tokens.py [--model ID] [--dry-run] <image> [...]

count_tokens is free to use but subject to requests-per-minute limits (Start tier: 5,000 RPM), and
its count is an estimate: https://platform.claude.com/docs/en/build-with-claude/token-counting
The key comes from a key file, as the reconstructor's spec 030 (FR-003) defines it: its path is
`--key-file`, else `DDON_LLM_KEY_FILE`, else `key_file` in `config.toml` in
`platformdirs.user_config_dir("ddon-llm")` (or `DDON_LLM_CONFIG_DIR`). No committed file names the
path. Before reading, the file's ACL (icacls) must grant read only to the user, SYSTEM and
Administrators; otherwise the script refuses (`key_acl`). The key is passed to the client in code
only: it is never printed, logged or put in an environment variable.
"""

import argparse
import base64
import io
import json
import math
import os
import pathlib
import subprocess
import sys
import tomllib

from PIL import Image

DEFAULT_MODEL = "claude-opus-5-5"
PROMPT = {"type": "text", "text": "Describe this image."}


ALLOWED_PRINCIPALS = ("NT AUTHORITY\\SYSTEM", "BUILTIN\\Administrators")


def key_path(cli: str | None) -> pathlib.Path:
    if cli:
        return pathlib.Path(cli)
    if os.environ.get("DDON_LLM_KEY_FILE"):
        return pathlib.Path(os.environ["DDON_LLM_KEY_FILE"])
    import platformdirs

    config_dir = pathlib.Path(os.environ.get("DDON_LLM_CONFIG_DIR") or platformdirs.user_config_dir("ddon-llm"))
    config = config_dir / "config.toml"
    if not config.is_file():
        sys.exit(f"unavailable: no_key (no --key-file, no DDON_LLM_KEY_FILE, no {config})")
    with config.open("rb") as handle:
        value = tomllib.load(handle).get("key_file")
    if not value:
        sys.exit(f"unavailable: no_key (no key_file in {config})")
    return pathlib.Path(value)


def check_acl(path: pathlib.Path) -> None:
    """Refuse a key file another principal can read (spec 030 review-P36)."""
    if os.name != "nt":
        if path.stat().st_mode & 0o077:
            sys.exit("unavailable: key_acl (mode is not 0600)")
        return
    user = f"{os.environ.get('USERDOMAIN', '')}\\{os.environ.get('USERNAME', '')}".lower()
    listing = subprocess.run(["icacls", str(path)], capture_output=True, text=True, check=True).stdout
    for line in listing.splitlines():
        entry = line.replace(str(path), "", 1).strip()
        if ":" not in entry or entry.startswith("Successfully"):
            continue
        principal = entry.split(":", 1)[0].strip()
        if principal.lower() != user and principal not in ALLOWED_PRINCIPALS:
            sys.exit(f"unavailable: key_acl ({principal} has access)")


def read_key(cli: str | None) -> str:
    path = key_path(cli)
    if not path.is_file():
        sys.exit("unavailable: no_key (the key file does not exist)")
    check_acl(path)
    return path.read_text(encoding="utf-8").strip()


def formula(width: int, height: int) -> int:
    """Visual tokens: one per 28x28 patch (platform.claude.com/docs/en/build-with-claude/vision)."""
    return math.ceil(width / 28) * math.ceil(height / 28)


def variants(img: Image.Image) -> dict[str, Image.Image]:
    w, h = img.size
    out = {"native": img}
    for tw in (960, 640):
        if tw < w:
            out[f"{tw}w"] = img.resize((tw, round(h * tw / w)), Image.LANCZOS)
    out["crop_center_half"] = img.crop((w // 4, h // 4, 3 * w // 4, 3 * h // 4))
    return out


def encode(img: Image.Image, fmt: str) -> bytes:
    buf = io.BytesIO()
    img.save(buf, fmt, **({"quality": 85} if fmt == "JPEG" else {"optimize": True}))
    return buf.getvalue()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("images", nargs="+")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--dry-run", action="store_true", help="print formula predictions only; no API call")
    parser.add_argument("--key-file", help="path of the API key file (else DDON_LLM_KEY_FILE, else the ddon-llm config)")
    args = parser.parse_args(argv)

    count = None
    baseline = None
    if not args.dry_run:
        import anthropic  # only needed for real counts

        client = anthropic.Anthropic(api_key=read_key(args.key_file), base_url="https://api.anthropic.com")

        def count(content: list[dict]) -> int:
            return client.messages.count_tokens(
                model=args.model, messages=[{"role": "user", "content": content}]).input_tokens

        baseline = count([PROMPT])

    for path in args.images:
        with Image.open(path) as opened:
            src = opened.convert("RGB")
        for name, img in variants(src).items():
            for fmt, media in (("PNG", "image/png"), ("JPEG", "image/jpeg")):
                data = encode(img, fmt)
                row = {"path": path, "variant": name, "w": img.width, "h": img.height, "bytes": len(data),
                       "format": fmt, "formula_tokens": formula(img.width, img.height), "model": args.model}
                if count is not None:
                    block = {"type": "image", "source": {"type": "base64", "media_type": media,
                                                         "data": base64.standard_b64encode(data).decode()}}
                    row["input_tokens"] = count([block, PROMPT])
                    row["image_tokens"] = row["input_tokens"] - baseline
                print(json.dumps(row), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
