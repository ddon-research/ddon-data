# Image input and token economy in Claude Code and Claude Desktop (R1)

Brief: `specs/004-vision-token-economy/brief-R1.md`. Researched 2026-10-17. Sources: Anthropic's
platform docs (fetched 2026-10-17), the `anthropics/claude-code` clone at
`D:/GitHub/anthropics/claude-code` (c017428c, 2026-10-16), the cookbooks clone at
`C:/ddon-dwarf-references/claude-cookbooks` (b2b0aa1f), the strings of the installed Claude Code
CLI `C:/Users/morph/.local/bin/claude.exe` (VERSION 2.1.296, SHA-256 `76de74f7...ff06769a`), and
ddon-hook at `C:/Users/morph/CLionProjects/ddon-hook` (5f06f6bc). No image was viewed: every
number below came from Pillow (`uv run --no-project --with pillow --with imagehash`) running the
scratchpad scripts `measure_shots.py`, `transcript_images.py` and `tool_of_images.py`.
"Inferred" marks conclusions that no source states directly.

## 1. The Vision API's accounting

**Token formula (current docs, all current models).** "Each patch is a 28×28-pixel block ... An
image, therefore, costs `⌈width / 28⌉ × ⌈height / 28⌉` visual tokens."
(https://platform.claude.com/docs/en/build-with-claude/vision, "Resolution and token cost"). The
older docs gave the approximation `width × height / 750` with a cap of about 1.15 megapixels for
pre-4.7 models. The computer use page still quotes "approximately 1.15 megapixels" for earlier
models (https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool, "Size
screenshots to fit image limits"). 750 is close to 28 × 28 = 784, so the two formulas differ by
about 4 % plus rounding. Use the patch formula.

**Resolution tiers** (same vision page, table "Resolution tier"):

| Tier | Models | Max long edge | Max visual tokens |
| --- | --- | --- | --- |
| High-resolution | Claude 4.7 and later | 2576 px | 4784 |
| Standard | all other models (e.g. Haiku 4.5, Opus 4.6 and earlier) | 1568 px | 1568 |

On the high-resolution tier, a 1920×1080 image is not resized and costs 2691 tokens. On the
standard tier it is resized to 1456×819 and costs 1560 tokens (same page, sizes table). The exact
resize rule is the largest aspect-preserving size that meets both the edge limit and the token
limit. The image is then padded on the bottom and right edges to a multiple of 28 px; padding
"contains no content" and is already part of the ceil formula
(https://platform.claude.com/docs/en/build-with-claude/vision-coordinates, "How Claude resizes and
pads images"; that page also has a reference implementation, reused in `measure_shots.py`).

**Per-request limits** (vision page, "Request limits"):

- 20 images per message on claude.ai.
- 100 images per API request for 200k-context models, 600 for all other models.
- 8000×8000 px maximum per image.
- If a request has more than 20 images, a stricter per-image limit applies; the docs say to keep
  both sides at or under 2000 px. Images nested in `tool_result` blocks and images resent from
  earlier turns count toward the 20.
- 10 MB base64 per image on the API, 5 MB on Bedrock and Vertex.
- 32 MB total request size, which "can be reached first".
- Formats are JPEG, PNG, GIF and WebP; only the first frame of an animation is used. Image
  metadata is not read (FAQ).

**File size, format, colour depth and compression do not change the token count.** The cost is
defined only by pixel dimensions (formula above). The docs present lossy compression as a way to
reduce *latency* and request size, and warn that "heavy JPEG compression can make text difficult
to read" (vision page, "Image quality guidance"). Inferred: greyscale, palette reduction or a
smaller PNG cost exactly the same tokens at the same dimensions. File size matters only for the
byte limits (10 MB per image, 32 MB per request) and for Claude Code's local byte budgets
(section 2).

**What changed in newer models:** the high-resolution tier (Claude 4.7 and later, which covers the
5.x models in use here) raises the cap from 1568 to 4784 tokens. "High-resolution images can use up
to roughly three times more visual tokens" (vision page). Two more changes: the API rejects
oversized computer-use and browser-use `tool_result` images instead of downscaling them (vision
page; vision-coordinates page, "Rescale coordinates"), and the opt-in
`transformations: {"oversized_image": "error"}` turns silent downscaling into a 400 error.

**Price context.** Opus 5.5 is $4 per million input tokens (vision page cost example). Cache
reads cost 0.05× base on Opus 5.5 and Sonnet 5.5, 0.025× on Fable 5.1 and Mythos 5.1, 0.1× on other
models. Cache writes cost 1.25× (5-minute TTL) or 2× (1-hour TTL). "Adding/removing images anywhere
in the prompt" invalidates the message-level cache
(https://platform.claude.com/docs/en/build-with-claude/prompt-caching).

**Third-party check.** https://www.developersdigest.tech/blog/claude-vision-api-production-guide
repeats the official formula, tiers and limits correctly. Its "1560 tokens" for 4K on the
standard tier matches the official table. These claims are its own and the official page does not
confirm them: "preprocessing cuts image costs 40 to 70 %" and "hash-based deduplication 10 to
25 %". Its practices that apply here: route resolution by content type (UI can be downscaled
aggressively, small text needs full resolution) and dedupe images by hash.

## 2. Claude Code specifics

**Read tool on an image.** Taken from the binary's strings (`claude.exe` 2.1.296):

- Default limits object `C0={maxWidth:2000,maxHeight:2000,maxBase64Size:5242880,targetRawSize:3932160}`
  (5 MiB base64, 3.75 MiB raw). Every model entry carries `image_limits:{maxWidth:2000,maxHeight:2000}`.
  Claude Code therefore caps images at 2000 px per side even on 2576-px models. The CHANGELOG
  explains why: 2.1.122 "Fixed images sent to newer models being resized to 2576px per side instead
  of the correct 2000px maximum" (`CHANGELOG.md:5838`). That is the many-image limit from item 1.
- The patch-token function is in the binary: `var It=28;function LRr(e,n){... Math.ceil(e/It)*Math.ceil(n/It)}`.
  When the display size's patch count exceeds the read token budget, the image is recompressed to
  a byte budget `floor(n/0.125)*0.75` (function `Gps`). The earlier base64-length estimate
  (`base64.length * 0.125`) caused heavy over-compression. That was issue #70010, closed
  2026-06-25 (https://github.com/anthropics/claude-code/issues/70010). Its example is a 1280×713
  screenshot: 1196 real tokens against a 74,243-token estimate.
- Compression ladder (binary strings):
  1. Resize to fit `maxWidth`/`maxHeight`.
  2. If the result is still over `targetRawSize`, try PNG `compressionLevel:9, palette:true`.
  3. Then JPEG quality 80 → 60 → 40 → 20.
  4. Then scale factors 1 / 0.75 / 0.5 / 0.25.
  5. Last resort: JPEG q20 at 400×400 or 600×600.

  Separate raw-byte budgets also exist: `hZ=512000` for local reads, and
  `imageMaxRawBytes:307200 / 512000` for remote transports.
- **Measured** in the ddon-hook transcript `ff8cf3d4-...jsonl` (see section 5):
  - 27 Reads of 1280×720 PNG screenshots (originals median 1.09 MB) reached the model as
    **1280×720 JPEG** (median 175 KB).
  - 3 small 1280×720 PNGs (around 60 KB) stayed PNG.
  - Inferred: PNGs over the ~500 KB local budget are re-encoded to JPEG at the same dimensions,
    so the token count is unchanged (1196) and only fidelity drops.
- Pasted and attached images use the same budget as Read since 2.1.97 (`CHANGELOG.md:6406`).
  Images over 128 MB are refused (2.1.302, `CHANGELOG.md:10`; that version is newer than the
  installed binary).
- Known side effect: issue #77729 (closed 2026-09-03) reported that Read overwrote the original
  file with a ~1200-px copy (https://github.com/anthropics/claude-code/issues/77729). Keep
  evidence screenshots read-only or let agents read copies (inferred precaution).

**Browser pane and computer-use screenshots.** This session's `mcp__Claude_Browser__computer`
schema and the binary carry the same text for the `scale` parameter. Its range is [0.1, 1]; "1
(default) uses the full image token budget, 0.5 returns an image at half the width and height
(~quarter of the tokens)". Coordinates stay in the full-resolution frame. The binary's
screenshot module defaults to `{pxPerToken:28,maxTargetPx:1568,maxTargetTokens:1568}`, with the
same binary search as Anthropic's reference resize. Inferred: a full browser screenshot costs at
most about 1568 tokens by default, unless a per-model override raises it. For the API computer-use
tool, Anthropic recommends 1024×768 or 1280×720 for desktop tasks and says to avoid resolutions
above 1920×1080. Screenshots cost "roughly 1,000–1,800 input tokens each", and "Dropping a
screenshot every turn changes the prefix every turn and invalidates the cache" (computer use page,
"Manage screenshot history"). `zoom` returns a region "scaled to fit within your usual screenshot
dimensions", so a zoom costs as much as a full screenshot (computer use page, actions table).

**How images age in context.** Every API call resends the whole conversation, and earlier images
stay in it (vision page, "Multiple images" and the Files API tip). In Claude Code they are served
from the prompt cache on every later call. An image is paid once as a cache write and then as a
cache read on every following call until compaction or session end. Changelog evidence:

- Compaction strips images and documents before summarizing (2.1.47, `CHANGELOG.md:7396`). Later
  the summarizer request kept images so that it could reuse the cache (2.1.70,
  `CHANGELOG.md:7118`). The summary that replaces the history is text. Inferred: images do not
  survive compaction.
- Oversized images in history are removed automatically and the request is retried (2.1.126,
  `CHANGELOG.md:5797`).
- Stripped images no longer prompt re-reads (2.1.147, `CHANGELOG.md:5321`).
- Prompt-cache misses occurred in screenshot-heavy sessions over the request size cap
  (2.1.257, `CHANGELOG.md:3079`).
- Issue #42256 reported one unprocessable image being resent on every message
  (https://github.com/anthropics/claude-code/issues/42256).

No public Claude Code doc gives image token budgets. Issue #45477 asked for them (closed
2026-08-07, https://github.com/anthropics/claude-code/issues/45477). Claude Desktop's code sessions
run the same Claude Code engine (inferred from the shared bundle and the changelog entries naming
"VS Code, desktop app, SDK", `CHANGELOG.md:283`). Desktop chat follows claude.ai's limits: 20
images per message, 10 MB each.

**Coordinates (vision-coordinates page).** Claude returns pixel coordinates "in the image Claude
sees", that is, after any resize. The page lists three ways to handle this:

- Pre-resize, so the image sent is exactly the image Claude sees.
- Recover the resized size with the reference function, then scale coordinates by the resized
  (not padded) dimensions.
- Mark the image `oversized_image: "error"`, so that drift fails loudly.

Small targets "lose precision when an image is downscaled"; the page's advice is to send a crop
and add the crop origin back to the returned coordinates. What this means for ddon-hook:

- At 1280×720, nothing resizes on either tier, and Claude Code's 2000-px cap does not apply. The
  coordinates an agent reads off a full shot are therefore client pixels.
- Any downscale or crop that ddon-hook performs must be written down next to the image: the scale
  factor, the crop origin and the original size. That record is what lets a click or a second
  crop be mapped back. The browser `scale` parameter does the same and keeps coordinates in the
  full-resolution frame.
- ddon-hook drives the client by keys, not clicks (`drive.py` `key`). Today coordinates matter
  only for choosing crops.

## 3. What ddon-hook does today

**Capture path.**

- `drive.py shot` (`scripts/automation/drive.py:82-89`) and scenario steps `shot` and
  `shot_every_s` (`scripts/automation/run_cycles.py:237-247`) send `{"cmd":"shot","path":...}` over
  the automation pipe.
- The DLL copies the next `Present`'s back buffer at full size: `GetBackBuffer`, an MSAA resolve,
  then `GetRenderTargetData` to system memory
  (`src/adapter/in/automation/d3d9_present_hook.cpp:47-97`).
- It writes the copy through WIC as PNG or BMP in 32bpp BGRA with default encoder options
  (`src/adapter/in/automation/image_encoder.cpp:38-94`, format at 54 and 72; contract
  `automation_command.hpp:21-22`).
- No resize, crop or quality option exists.
- `ddo_window.py` (`scripts/automation/ddo_window.py:59-94`) is a fallback that uses PrintWindow
  and writes RGB PNG with zlib level 6.
- `evidence_capture_service.cpp:500-520, 908-920` only logs the game's own screenshot functions
  (`sCapture::outputBmp`, `sScreenShot::moveMain` JPEG sizes). It captures no pixels for agents.

**Measured** (`measure_shots.py` over `build/automation-runs/` and `build/automation-drive/`):

- 114 files, all **1280×720 PNG, RGBA**.
- Size: min 5.3 KB, median 1.09 MB, max 1.89 MB; 115 MB in total.
- Token cost: **1196 tokens per image** on both tiers. That is the patch count 46 × 26, and there
  is no resize because 1280×720 is under both caps.
- 18 of 114 consecutive frames are near-duplicates (pHash distance ≤ 4).
- `C:\DDON` holds unrelated ReShade screenshots from 2025; not used.

**Re-encode experiments.** File sizes in bytes; tokens depend only on the dimensions.

| Frame | Original PNG | PNG optimised | PNG 256-colour | PNG grey | JPEG q85 | WebP q80 | Tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 000-boot | 59,665 | 49,212 | 19,667 | 21,112 | 43,210 | 15,920 | 1196 |
| 006-soak | 925,980 | 751,005 | 326,128 | 261,245 | 109,070 | 66,306 | 1196 |
| 011-in-world | 1,888,533 | 1,578,602 | 547,302 | 539,685 | 262,786 | 176,314 | 1196 |

The answer to Sam's question: compressing the file 10× saves **zero tokens**. It only keeps a
frame under Claude Code's ~500 KB local budget, so the frame arrives as Sam's PNG instead of
Claude Code's own JPEG re-encode. Inferred: it does save request bytes and latency.

## 4. Cheaper alternatives, ranked by tokens saved per decision

The baseline is one full 1280×720 shot per decision: 1196 tokens when first read, plus a cache
read at 0.05× on every later call while the image stays in context.

1. **No pixels; text state from hooks, pipe and server log.** About 1196 → 20-100 tokens, a saving
   of over 90 %. Two text sources already exist:
   - `status` gives presents, window, `app_active`, the spoof state and input isolation
     (`automation_command.hpp:10-19`).
   - `drive.py log <regex>` gives the server-log lines since the last call (`drive.py:97-106`).

   Inferred: one JSON line holding stage, the state of an open dialog or menu, the quest flags and
   the player position would answer most "where am I, what's open" decisions. The candidate
   sources are the existing game hooks and evidence store, or memory reads.
2. **Template match or perceptual hash in the driver; image only on mismatch.** Expected cost per
   decision = p(mismatch) × 1196. With a 10 % mismatch rate that is about 120 tokens. 18 of 114
   measured frames already duplicate their predecessor, and those frames should never reach an
   agent. Libraries: `imagehash` (pHash, used here) or OpenCV `matchTemplate` against reference
   crops of known dialogs.
3. **Crop to the region of interest.** A centre crop of 640×360 costs 299 tokens (−75 %). A dialog
   of about 420×200 costs 15 × 8 = 120 tokens (−90 %). Cropping keeps full detail, unlike
   downscaling. Record the crop origin (section 2, coordinates).
4. **OCR in the driver.** A dialog's text costs tens of tokens instead of 1196. Inferred: the game
   font on a 720p frame needs checking. Use a library, for example Windows.Media.Ocr through
   `winrt` or Tesseract via `pytesseract`, and fall back to a crop when confidence is low.
5. **Downscale the whole frame.** 960×540 costs 700 tokens (−41 %); 640×360 costs 299 (−75 %). Use
   it for layout and scene questions only. Small UI text becomes unreliable, and the docs warn
   about legibility. The browser `scale: 0.5` gives about −75 % the same way.
6. **Contact sheet.** Nine 427×240 thumbnails in one 1281×720 image cost 1196 tokens in total,
   against 9 × 1196 = 10,764 for separate frames (−89 %). Each thumbnail gets about 133 tokens, so
   a sheet suits "what happened over this soak" timelines, not text. It also stays under the
   more-than-20-images limit (section 1).
7. **Greyscale, palette reduction, JPEG or WebP.** **0 tokens saved** (section 1). Use them only to
   stay under the ~500 KB budget and the 32 MB request limit.

Delegation multiplies these savings. The coordinator rule already sends sweeps to a subagent
whose conclusions alone return (`D:/ddon-data/CLAUDE.md`, "Delegation"). Inferred: an agent
that views frames inside a subagent keeps the frames' cache reads out of the long-lived main
context.

## 5. Recommendations for ddon-hook

1. **Capture format.** Keep full 1280×720 PNG as the evidence archive; it is exact, and storage is
   cheap. Add a second, agent-facing output written by the driver (Python + Pillow, not the DLL):
   - by default, a crop of the region the step cares about;
   - otherwise, a full frame at 960×540 or 640×360;
   - as optimised PNG (or palette PNG) kept under 500 KB, so that Claude Code does not re-encode
     it to JPEG.

   Write a sidecar line with `{src, crop_origin, scale, w, h, tokens}`. Never point Read at the
   evidence original (issue #77729).
2. **What the driver emits as text.** After every `key` and `shot`, print one JSON line:
   - the `status` fields;
   - the new server-log lines that match the step;
   - the pHash distance to the previous frame and to the expected reference frame;
   - a `match` verdict per known screen (title, login, character select, in-world, the dialog
     open);
   - OCR text of the dialog region, when present.

   The scenario format can carry the expected-screen name per `shot` step.
3. **When an agent looks at pixels.** Only when one of these holds:
   - the template or hash verdict is `mismatch` or `unknown`;
   - the OCR confidence is low;
   - a step is being designed for the first time (`drive.py` exploration).

   Then the agent views a crop first and the full frame only if the crop is ambiguous. A whole soak
   is summarised as one contact sheet. Prefer doing the viewing in a subagent.
4. **Measurement.** `.agent-ledger/usage-readings.jsonl` holds plan percentages only (one row:
   `weekly`, `five_hour`), so measure from the transcripts instead:
   - Baseline: the ddon-hook transcript `C:/Users/morph/.claude/projects/C--Users-morph-CLionProjects-ddon-hook/ff8cf3d4-251f-42e0-b8ea-f1db8fbab407.jsonl`.
   - It made 596 API calls and has no compaction markers.
   - Usage: input 1,294; cache_creation 712,283; cache_read 258,422,417; output 311,826.
   - It holds 52 images, all from Read: 27 × 1280×720 JPEG re-encodes, 3 × 1280×720 PNG, 13 ×
     640×400, 4 × 800×500, 2 × 2000×563, 2 × 720×300 and 1 × 960×96. Together they cost 46,189
     tokens on first read.
   - Upper bound on their later cache reads: 6.47 M tokens (about 2.5 % of all cache reads).
   - At Opus 5.5 rates, the cache reads are about 0.32 M input-equivalent against about 58 K for
     the cache writes. **Residence in context, not the first read, dominates an image's cost.**
     Images are a minor share of this session, but per decision they are the most compressible.

   To confirm the savings, rerun `transcript_images.py` on the next drive session and compare images
   per decision, image tokens and the reread bound. A bounded `jq` equivalent of the usage totals:

   ```sh
   jq -c 'select(.type=="assistant") | .message | {id, u: .usage}' <transcript.jsonl> \
     | jq -s 'unique_by(.id) | map(.u) | {calls: length,
         cache_read: (map(.cache_read_input_tokens // 0) | add),
         cache_write: (map(.cache_creation_input_tokens // 0) | add)}'
   ```

   Success means fewer than 0.3 full-frame images per decision and image tokens per run down by at
   least 70 %, with the same scenario pass rate. Not run yet: there is no post-change session.
5. **Per-image check with `count_tokens`.** Source:
   https://platform.claude.com/docs/en/build-with-claude/token-counting. The endpoint accepts base64
   images and is free, but rate limited (Start tier: 5,000 RPM). It returns only a total
   `input_tokens`.
   - It is "an **estimate**" that "might differ by a small amount".
   - It may include system-added tokens that are not billed.
   - It does not use caching.
   - Per the vision-coordinates page, it estimates an image "from its dimensions without fully
     processing it".

   So it is not an exact meter: it is the server's own statement of the dimension formula.

   **The script.** `research/claude-vision/count_image_tokens.py` (PEP 723 metadata: `anthropic`
   and `pillow`) builds four variants of each path in memory with Pillow:
   - native size;
   - 960 px wide;
   - 640 px wide;
   - a centre-half crop.

   It encodes each variant as PNG and as JPEG q85 and prints one JSON line per variant: `path`,
   `variant`, `w`, `h`, `bytes`, `format`, `formula_tokens`, and with the API also `input_tokens`
   and `image_tokens`. `image_tokens` is count(image + text) − count(text); the text-only baseline
   is counted once. The key comes only from `ANTHROPIC_API_KEY`, read by the SDK. The default
   model is `claude-opus-5-5`, overridable with `--model`.

   Sam runs it as `uv run research/claude-vision/count_image_tokens.py <shot.png> ...`.

   **Dry run (done).** `--dry-run` prints the predictions without calling the API. It ran on two
   real shots from `build/automation-runs/`:
   - `20261017T211114/002-title.png`: 14 KB PNG.
   - `20261017T203009/003-0142s.png`: 705 KB PNG.

   Both predict 1196 / 700 / 299 / 299 tokens for the four variants, the same for PNG and JPEG,
   while the bytes range from 6 KB to 705 KB. The API mode has not run here; spending needs Sam.
   The exact billed figure stays the Messages `usage` delta between two otherwise identical
   requests, and that costs money.

## Sources used

Every page, clone and binary cited above has a row in `research/external-references.jsonl`
(rows dated 2026-10-17). Cookbook support: `multimodal/crop_tool.ipynb:234-258` returns zoom crops
as JPEG to stay under 32 MB, and `cost_optimization/cost_optimization.ipynb:1265` calls 1280×720
"a safe default that caps every image at ~1,200 tokens". The SDK clones were not needed.
