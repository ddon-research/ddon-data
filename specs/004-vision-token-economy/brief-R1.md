# R1 Image input and token economy in Claude Code and Claude Desktop

Role: general-purpose researcher (web, local code, measurements). Time budget: 45 minutes of wall
clock. Read-only everywhere except the output file, scratchpad files and new rows in
`D:\ddon-data\research\external-references.jsonl` (format: `research/external-references.md`).

## Question

How do Claude Code and Claude Desktop turn image input (Read of a PNG/JPEG, screenshots from the
browser and computer-use tools, images in tool results) into tokens, and what is the cheapest way
for ddon-hook's client automation to give an agent the visual information it needs?

## Context

ddon-hook (`C:\Users\morph\CLionProjects\ddon-hook`) automates the DDO client (spec 011). The
client renders at some resolution; the proxy DLL captures screenshots in-process, and Python
scripts drive runs: `scripts/automation/{drive.py,run_cycles.py,ddo_window.py}`, plus the evidence
capture code in `src/core/usecase/evidence_capture_service.cpp` and
`src/adapter/out/evidence/jsonl_evidence_store.cpp`. Agents then read the screenshots. Sam suspects
they are captured at high quality and wonders whether file-size optimization saves tokens.

## Cover

1. **The Vision API's accounting**, from Anthropic's documentation (cite each URL, with the model
   generation it applies to): the token formula, the maximum dimensions and megapixels before
   downscaling, the per-request image limits, whether file size, format (PNG/JPEG/WebP/GIF), colour
   depth or compression change the token count, and whether newer models (Claude 4.x / 5) changed
   any of this.
2. **Claude Code specifics:** what the Read tool does with an image (resizing, limits), how
   screenshots from the browser tools and computer use are scaled (the `scale` parameter of the
   screenshot and zoom actions), how images in context age (do they stay in every later turn's
   cache read; does compaction drop them), and what the docs or the Claude Code GitHub issues say on
   image token cost. Use the `claude-code-guide` knowledge only through public docs; clone
   `anthropics/claude-code` into `D:/GitHub/anthropics/claude-code` if its issues or docs help
   (AGENTS.md "Clone what you analyse").
3. **What ddon-hook does today:** read the capture code and scripts. Give the resolution, format,
   compression and size of real screenshots from its run logs (find them with `fd -e png -e bmp
   -e jpg` under the repo's run and log folders, and under `C:\DDON` if logs are there; measure with a
   library such as Pillow via `uv run --with pillow`, never by reading images into your context).
   Compute the token cost per image with the formula from item 1.
4. **Cheaper alternatives, ranked by tokens saved per decision**, with rough numbers:
   - downscaling and cropping to the region of interest (a dialog, a menu);
   - greyscale or palette reduction, if it changes nothing for tokens (say so);
   - text instead of pixels: reading game state from memory or hooks, OCR in the driver, a
     structured scene summary, perceptual hashes or template matching against reference images so
     an agent only sees an image on a mismatch;
   - batching: one contact sheet of thumbnails versus several images.
5. **Recommendations for ddon-hook**, concrete: the capture size and format, what the driver should
   emit as text, when an agent should look at pixels at all, and a measurement to confirm the
   savings (tokens per run from the usage logs, `.agent-ledger/usage*.jsonl` or the transcripts'
   `usage` fields, with bounded `jq`).

## Output

`D:\ddon-data\research\claude-vision-tokens.md`, at most 350 lines: one section per item, each
claim with its source URL or file and line, inferences marked. Do not commit. Never view more than
two images yourself; measure them with code. Leave no background shells running. Final message:
the path, line count and the five most important findings in at most ten lines.
