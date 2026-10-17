# /// script
# requires-python = ">=3.14"
# dependencies = ["anthropic", "pillow"]
# ///
"""Count the image tokens of screenshots with Anthropic's count_tokens endpoint.

For each image path: native size plus the variants from research/claude-vision-tokens.md item 4
(downscaled to 960 and 640 px wide, a centre-half crop), each encoded in memory as PNG and as
JPEG q85. One JSON line per variant, with the patch formula's prediction alongside.

  uv run research/claude-vision/count_image_tokens.py [--model ID] [--dry-run] <image> [...]

count_tokens is free to use but subject to requests-per-minute limits (Start tier: 5,000 RPM), and
its count is an estimate: https://platform.claude.com/docs/en/build-with-claude/token-counting
The key comes only from the ANTHROPIC_API_KEY environment variable, read by the SDK itself.
"""

import argparse
import base64
import io
import json
import math
import sys

from PIL import Image

DEFAULT_MODEL = "claude-opus-5-5"
PROMPT = {"type": "text", "text": "Describe this image."}


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
    args = parser.parse_args(argv)

    count = None
    baseline = None
    if not args.dry_run:
        import anthropic  # only needed for real counts

        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

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
