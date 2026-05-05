---
name: photo-to-codex-pet
description: Turn an uploaded or local person photo into a configured Codex desktop pet. Use when a user wants to upload a portrait, choose cartoon or photo-faithful realistic style, generate a consistent character likeness, create Codex-compatible animated pet spritesheets, package pet.json and spritesheet.webp, and install the result under ${CODEX_HOME:-$HOME/.codex}/pets so it appears in the Codex desktop pet picker.
---

# Photo To Codex Pet

## Overview

Use this skill to create a Codex desktop pet from a person photo. The workflow supports two visual modes:

- `cartoon`: compact chibi / pixel-adjacent Codex pet style.
- `realistic`: photo-faithful mode that should preserve the source photo as directly as possible while completing any missing body parts conservatively. Default to a foreground cutout made from the original photo for the visible face, hair, and outfit, then infer only the missing lower body from the visible clothing so the pet reads as a complete desktop character. Do not redraw the face or restyle the person unless the user explicitly asks for generated/repainted art.

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

4. For `realistic`, first attempt a photo-faithful cutout workflow before using `$imagegen`.

Use the original photo pixels as the canonical identity whenever possible:

- Remove the background from the source photo with a mask, chroma key, segmentation, or other local image-processing method.
- Preserve the original face, hair, outfit, colors, texture, and expression from the photo.
- If the photo is a bust, ID photo, or half-body portrait, keep the visible face, hair, and torso as source-photo cutout pixels, then complete the missing lower body conservatively from the visible outfit. For example, a black blazer and white shirt can continue into a matching dark skirt/trousers, simple legs, socks, and shoes.
- The completed lower body must be subordinate to the photo cutout: it should match the visible outfit colors and lighting, avoid new fashion choices, and never alter the face or upper-body identity.
- Place the completed full-body or bust-plus-completed-body pet on transparent background inside each `192x208` cell.
- For actions, prefer subtle pose transforms, small attached props, and slight offsets over facial redrawing. Keep the face unchanged unless the user explicitly wants expressive repainting.
- If the background cannot be removed cleanly, stop and explain the blocker or use `$imagegen` only as a fallback with the prompt requiring maximum photo fidelity.

The cutout should be saved as:

```text
<run-dir>/references/canonical-base.png
```

5. For `cartoon`, or when `realistic` cutout is impossible and the user accepts generated art, generate the base character with `$imagegen`.

Use the prompt written to:

```text
<run-dir>/prompts/base-character.md
```

Attach the uploaded/local photo as the reference image. The output should be a full-body pet character on a flat chroma-key background. Do not include text, logos, scenery, shadows, or UI. In `realistic` fallback generation, explicitly preserve the original photo identity and outfit instead of redesigning the person.

6. Record or copy the selected base image into the pet run as the canonical visual reference. If continuing through `$hatch-pet`, use its normal `record_imagegen_result.py` workflow. If adapting manually, keep the base image under:

```text
<run-dir>/references/canonical-base.png
```

7. Generate action images or action rows using the prompts written under:

```text
<run-dir>/prompts/actions/
```

Attach both the original photo and `canonical-base.png` for each action prompt. The action images should preserve the same identity and outfit while changing pose, mood, or small held prop. For `realistic` cutout mode, action rows should keep the original face and source-photo pixels as much as possible; do not redraw expressions such as anger or happiness if doing so harms likeness.

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
Default behavior: preserve the source photo pixels through foreground cutout and transparency cleanup, not generative redrawing.
Match the person's visible appearance as closely as possible: face shape, hairstyle, hair volume and parting, glasses shape, expression, skin tone impression, clothing, colors, tie, suit texture, and overall posture.
If the input photo is a headshot, ID photo, or half-body portrait, keep the visible face, hair, and torso as source-photo cutout pixels, then complete the missing lower body conservatively from the visible clothing. Do not leave the pet as only a floating bust when the user asks for a desktop pet character.
Keep natural proportions and recognizable likeness. Do not chibi-fy, do not make the eyes oversized, do not turn the subject into an anime mascot, do not invent a different outfit, and do not repaint the face unless explicitly requested. Any inferred lower body should be plain, matching, and less visually important than the original photo cutout.
Centered complete character, generous padding, transparent-ready.
No scenery, no text. Remove the source background instead of replacing the subject.
```

For `realistic`, it is preferable for the pet to look like a clean photo cutout/avatar with a conservatively completed body rather than a cartoon. The final atlas must remain readable at desktop-pet size, but likeness takes priority over adding exaggerated animation or expressions.

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
