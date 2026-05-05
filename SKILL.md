---
name: photo-to-codex-pet
description: Turn an uploaded or local person photo into a configured Codex desktop pet. Use when a user wants to upload a portrait, choose cartoon or photo-faithful realistic style, generate a consistent character likeness, create Codex-compatible animated pet spritesheets, package pet.json and spritesheet.webp, and install the result under ${CODEX_HOME:-$HOME/.codex}/pets so it appears in the Codex desktop pet picker.
---

# Photo To Codex Pet

## Overview

Use this skill to create a Codex desktop pet from a person photo. The workflow supports two visual modes:

- `cartoon`: compact chibi / pixel-adjacent Codex pet style.
- `realistic`: photo-faithful mode that should create a coherent full-body realistic person image based on the source photo. Default to an image-generation/editing workflow that uses the source photo as the identity reference, reconstructs a complete natural full-body portrait, and keeps the face, hair, outfit style, colors, and expression as close to the photo as possible. Do not make a simple local collage such as "photo head plus drawn body" except as an explicitly labeled emergency fallback.

This skill composes two existing capabilities:

- `$imagegen` for generating a clean base character and grounded animation rows.
- `$hatch-pet` or `${CODEX_HOME:-$HOME/.codex}/skills/hatch-pet` scripts for Codex pet atlas assembly, validation, previews, and packaging.

## Inputs

Required:

- A person photo, either uploaded in the conversation or available as a local file path.
- A style choice: `cartoon` or `realistic`. If omitted, ask once; default to `cartoon` only when the user asked you to proceed without questions.

Optional:

- Pet name.
- Short personality or accessory notes.
- Semantic action set, such as `办公,休息,思考,游戏,度假,开心,生气`. If omitted, use those seven defaults.
- Output folder. Default to `${CODEX_HOME:-$HOME/.codex}/pet-runs/<slug>` for the run and `${CODEX_HOME:-$HOME/.codex}/pets/<slug>` for the installed pet.

## Workflow

1. If the photo is a local path, inspect it with the available image-viewing tool before using it as an image generation reference.
2. Ask for `cartoon` or `realistic` if the user did not choose.
3. Create a run folder with the helper script:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/photo-to-codex-pet/scripts/start_photo_pet_run.py" \
  --photo /absolute/path/to/person-photo.png \
  --pet-name "<Name>" \
  --pet-id "<ascii-id>" \
  --style cartoon \
  --actions "办公,休息,思考,游戏,度假,开心,生气"
```

Use `--style realistic` for the photo-faithful realistic path.

Use `--pet-id` when the display name contains non-ASCII characters. For example, use `--pet-name "小明2号" --pet-id xiaoming2`.

4. For `realistic`, first attempt a photo-faithful full-body image generation/editing workflow with `$imagegen`.

Use the original photo as the canonical identity reference:

- Generate a single coherent, natural full-body realistic character portrait, not a pasted-together composite.
- Match the source face, hairline, bangs, hair length, skin tone impression, expression, visible clothing, colors, tie/bow, suit texture, and overall identity.
- If the source is a bust, ID photo, or half-body portrait, infer the missing lower body from the visible outfit so the result is a complete person in the same style, lighting, and camera language.
- The full body must look like one unified photo or clean realistic avatar. Avoid visible seams, mismatched scale, mismatched lighting, stiff pasted legs, or hand-drawn lower-body shortcuts.
- Use a transparent-ready flat chroma-key background or transparent background if the tool supports it.
- For actions, generate or edit coherent full-body action poses from the same canonical full-body image. Keep the face and identity consistent; use small props only when needed.
- Use local cutout/body-completion only when image generation is unavailable. If using that fallback, clearly tell the user it is not the intended high-quality realistic path.

The generated full-body canonical image should be saved as:

```text
<run-dir>/references/canonical-base.png
```

5. For `cartoon`, generate the base character with `$imagegen`.

Use the prompt written to:

```text
<run-dir>/prompts/base-character.md
```

Attach the uploaded/local photo as the reference image. The output should be a full-body pet character on a flat chroma-key background. Do not include text, logos, scenery, shadows, or UI. In `realistic`, explicitly preserve the original photo identity and outfit instead of redesigning the person, while making the whole body coherent.

6. Record or copy the selected base image into the pet run as the canonical visual reference. If continuing through `$hatch-pet`, use its normal `record_imagegen_result.py` workflow. If adapting manually, keep the base image under:

```text
<run-dir>/references/canonical-base.png
```

7. Generate action images or action rows using the prompts written under:

```text
<run-dir>/prompts/actions/
```

Attach both the original photo and `canonical-base.png` for each action prompt. The action images should preserve the same identity and outfit while changing pose, mood, or small held prop. For `realistic`, action rows should look like the same full-body person in a coherent realistic style; do not create a pasted-photo face on a mismatched drawn body.

8. Continue through `$hatch-pet` to generate or assemble animation rows, build the `1536x1872` atlas, validate, render QA, and package:

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
  pet.json
  spritesheet.webp
```

9. Validate before final delivery:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/hatch-pet/scripts/validate_atlas.py" \
  "${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/spritesheet.webp" \
  --json-out "${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/_conversion_qa/validation.json"
```

10. Generate a contact sheet preview when the script is available:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/hatch-pet/scripts/make_contact_sheet.py" \
  "${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/spritesheet.webp" \
  --output "${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/_conversion_qa/contact-sheet.png"
```

11. Tell the user to restart Codex App or reopen the desktop pet picker if it does not appear immediately.

## Action Generation

The default semantic actions are:

```text
办公, 休息, 思考, 游戏, 度假, 开心, 生气
```

The helper script writes one prompt per action under `<run-dir>/prompts/actions/`. Each action prompt should be generated with the original photo plus the canonical base image attached. Keep the action readable at desktop-pet size.

Recommended action rules:

- Keep identity locked: same face, hair, glasses, outfit, colors, and silhouette.
- Use small held props only when needed, such as a laptop/document for `办公` or a game controller for `游戏`.
- Avoid full environments. Do not generate office rooms, beaches, beds, game screens, UI, readable text, or large furniture.
- Avoid detached symbols such as question marks, anger icons, sparkles, speech bubbles, floating charts, and light bulbs.
- Keep each action on a flat chroma-key background so it can be converted to transparency.

When mapping semantic actions into Codex's fixed 9-row atlas, prefer:

```text
idle          <- standing/default or 开心
running-right <- motion variant, or generic locomotion from base
running-left  <- mirrored running-right when appropriate
waving        <- 开心 or greeting
jumping       <- 开心 or energetic
failed        <- 生气
waiting       <- 休息 or 思考
running       <- generic locomotion
review        <- 办公 or 思考
```

Extra actions such as `游戏` and `度假` can be included as alternate rows, preview assets, or used to replace the least relevant fixed row when the user explicitly prefers them.

## Prompt Rules

For `cartoon`, preserve recognizable high-level identity from the photo, but simplify:

```text
Create a compact chibi Codex desktop pet character based on the reference person photo.
Preserve the person's broad visual identity cues: hairstyle, face shape impression, glasses if present, and signature clothing colors if visible.
Use pixel-art-adjacent edges, thick dark outline, flat cel shading, small readable face, tiny limbs, and a limited palette.
Full body, centered, generous padding.
Perfectly flat solid chroma-key background, no shadows, no scenery, no text.
```

For `realistic`, maximize fidelity to the photo. This mode should not redesign the person into a generic avatar. Preserve the reference as directly as possible:

```text
Create a photo-faithful Codex desktop pet from the reference person photo.
Default behavior: use the source photo as a reference to generate/edit one coherent full-body realistic portrait, not a simple pasted collage.
Match the person's visible appearance as closely as possible: face shape, hairstyle, hair volume and parting, glasses shape, expression, skin tone impression, clothing, colors, tie, suit texture, and overall posture.
If the input photo is a headshot, ID photo, or half-body portrait, infer the missing lower body conservatively from the visible clothing, but the result must look like one unified photo/realistic avatar. Do not leave the pet as only a floating bust, and do not paste a photo head onto a mismatched drawn body.
Keep natural proportions and recognizable likeness. Do not chibi-fy, do not make the eyes oversized, do not turn the subject into an anime mascot, do not invent a different outfit, and do not repaint the person into a different identity.
Centered complete character, generous padding, transparent-ready.
No scenery, no text. Remove the source background instead of replacing the subject.
```

For `realistic`, it is preferable for the pet to look like a coherent full-body photo/realistic avatar rather than a cartoon or collage. The final atlas must remain readable at desktop-pet size, but likeness and whole-body coherence take priority over exaggerated animation or expressions.

## Configuration

The completed pet is configured by writing `pet.json` and `spritesheet.webp` under:

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
```

Use portable paths in instructions and scripts. Do not hardcode one user's home directory in reusable guidance.

## Privacy And Safety

- Use the photo only as a visual reference for the user's requested local pet.
- Do not identify the person in the photo unless the user explicitly provides the identity.
- For public figures, avoid implying endorsement; make a stylized pet inspired by the supplied image.
