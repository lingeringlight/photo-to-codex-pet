#!/usr/bin/env python3
"""Prepare a reproducible photo-to-Codex-pet run folder."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or "~/.codex").expanduser().resolve()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "photo-pet"


def style_notes(style: str) -> str:
    if style == "realistic":
        return (
            "Photo-faithful realistic Codex desktop pet mode. Match the source photo as closely "
            "as possible: face shape, hairstyle, glasses, expression, skin tone impression, outfit, "
            "colors, posture, and clothing details. Use natural proportions and realistic-to-clean "
            "avatar rendering. Do not chibi-fy, do not enlarge the eyes, do not convert to anime, "
            "and do not invent a different outfit. Only simplify enough for a readable transparent "
            "desktop pet sprite."
        )
    return (
        "Cartoon chibi Codex desktop pet style, pixel-art-adjacent stepped edges, thick dark "
        "outline, compact proportions, flat cel shading, limited palette, readable at small size."
    )


DEFAULT_ACTIONS = ["办公", "休息", "思考", "游戏", "度假", "开心", "生气"]


ACTION_SPECS = {
    "办公": {
        "english": "working at a desk",
        "pose": "focused office-working pose, seated or standing with a small laptop or document held close to the body",
        "avoid": "large desks, room backgrounds, visible text, UI screens, floating charts",
    },
    "休息": {
        "english": "resting",
        "pose": "relaxed resting pose, eyes softened, shoulders relaxed, optionally holding a small cup or pillow close to the body",
        "avoid": "beds, large furniture, full room scenery, detached sleep symbols",
    },
    "思考": {
        "english": "thinking",
        "pose": "thoughtful pose with one hand near chin, slight head tilt, focused expression",
        "avoid": "floating question marks, light bulbs, text, speech bubbles",
    },
    "游戏": {
        "english": "gaming",
        "pose": "playful gaming pose holding a small game controller close to the body, energetic stance",
        "avoid": "TV screens, game UI, logos, readable console branding, room scenery",
    },
    "度假": {
        "english": "vacation",
        "pose": "vacation mood pose with relaxed smile, optional tiny sunglasses or small travel cup, outfit identity still preserved",
        "avoid": "beaches, scenery, palm trees, large luggage, background props",
    },
    "开心": {
        "english": "happy",
        "pose": "happy celebratory pose, bright smile, lifted arms or confident upbeat stance",
        "avoid": "detached sparkles, confetti, text, floating symbols",
    },
    "生气": {
        "english": "angry",
        "pose": "angry or annoyed reaction pose, furrowed brow, clenched small fists, body leaning forward slightly",
        "avoid": "anger symbols, flames, text, violence, weapons",
    },
}


def parse_actions(raw: str) -> list[str]:
    actions = [item.strip() for item in re.split(r"[,，]", raw) if item.strip()]
    return actions or DEFAULT_ACTIONS


def action_prompt(name: str, style: str, action: str, notes: str) -> str:
    spec = ACTION_SPECS.get(
        action,
        {
            "english": action,
            "pose": f"clear {action} themed pose",
            "avoid": "text, scenery, detached decorative symbols, large props",
        },
    )
    identity_lock = (
        "Preserve the same person identity from the canonical base and source photo: face shape, "
        "hairstyle, glasses, expression family, clothing, colors, proportions, and silhouette. "
        "Do not redesign the character."
        if style == "realistic"
        else "Preserve the same stylized character identity from the canonical base: hairstyle, glasses if present, outfit colors, face impression, proportions, and silhouette."
    )
    style_line = style_notes(style)
    return f"""Use case: stylized-concept
Asset type: action row concept for a Codex desktop pet
Primary request: Create the '{action}' / {spec['english']} action for the pet named {name}.
Identity lock: {identity_lock}
Action: {spec['pose']}.
Style notes: {style_line}
User notes: {notes or "None."}
Composition: full-body character centered with generous padding. Keep any prop small, attached to or held by the character, and inside the sprite frame.
Background: perfectly flat solid #00ff00 chroma-key background for background removal. No shadows, gradients, scenery, floor plane, or lighting variation.
Avoid: {spec['avoid']}; no watermark, no logo, no text.
"""


def base_prompt(name: str, style: str, notes: str) -> str:
    mode = "photo-faithful realistic desktop pet cutout/avatar" if style == "realistic" else "cartoon chibi desktop pet"
    if style == "realistic":
        subject = (
            "Full-body realistic desktop pet character based directly on the reference person photo. "
            "Maximize likeness and photo fidelity. Match the visible face shape, hairstyle, hair volume "
            "and parting, glasses shape, expression, skin tone impression, clothing, colors, suit texture, "
            "tie, and overall posture. If the photo is a headshot or half-body portrait, infer missing lower "
            "body conservatively from the visible outfit without changing identity. Do not identify the person "
            "or add text."
        )
        avoid = (
            "no text, no watermark, no logo, no scenery, no cast shadow, no detached decorative effects, "
            "no chibi proportions, no oversized eyes, no anime redesign, no different outfit, no glossy 3D render."
        )
    else:
        subject = (
            "Full-body pet character inspired by the reference person. Preserve broad identity cues such as "
            "hairstyle, face shape impression, glasses if present, clothing color impression, and overall "
            "friendly presence. Do not identify the person or add text."
        )
        avoid = (
            "no text, no watermark, no logo, no scenery, no cast shadow, no detached decorative effects, "
            "no glossy 3D render, no busy tiny details."
        )
    return f"""Use case: stylized-concept
Asset type: canonical base character for a Codex desktop pet
Primary request: Create a {mode} based on the attached reference person photo.
Subject: {subject}
Pet name: {name}
Style notes: {style_notes(style)}
User notes: {notes or "None."}
Composition: one full-body character centered, front-facing 3/4 pose, generous padding, no cropping.
Background: perfectly flat solid #00ff00 chroma-key background for background removal. The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation. Do not use #00ff00 anywhere in the subject.
Avoid: {avoid}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--photo", required=True, help="Path to the person photo reference.")
    parser.add_argument("--pet-name", required=True)
    parser.add_argument(
        "--pet-id",
        help="Stable ASCII package id and folder name. Recommended when --pet-name contains non-ASCII characters.",
    )
    parser.add_argument("--style", choices=["cartoon", "realistic"], required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument(
        "--actions",
        default=",".join(DEFAULT_ACTIONS),
        help="Comma-separated semantic actions to generate prompts for. Default: 办公,休息,思考,游戏,度假,开心,生气.",
    )
    parser.add_argument("--run-dir", help="Defaults to ${CODEX_HOME:-$HOME/.codex}/pet-runs/<slug>.")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    photo = Path(args.photo).expanduser().resolve()
    if not photo.exists():
        raise SystemExit(f"photo not found: {photo}")

    slug = slugify(args.pet_id or args.pet_name)
    run_dir = Path(args.run_dir).expanduser().resolve() if args.run_dir else codex_home() / "pet-runs" / slug
    if run_dir.exists() and not args.force:
        raise SystemExit(f"run dir already exists: {run_dir}; pass --force to overwrite metadata")

    references = run_dir / "references"
    prompts = run_dir / "prompts"
    references.mkdir(parents=True, exist_ok=True)
    prompts.mkdir(parents=True, exist_ok=True)

    photo_copy = references / f"person-reference{photo.suffix.lower() or '.png'}"
    shutil.copy2(photo, photo_copy)

    prompt_path = prompts / "base-character.md"
    prompt_path.write_text(
        base_prompt(args.pet_name, args.style, args.notes),
        encoding="utf-8",
    )
    actions = parse_actions(args.actions)
    action_prompt_paths: dict[str, str] = {}
    actions_dir = prompts / "actions"
    actions_dir.mkdir(parents=True, exist_ok=True)
    for index, action in enumerate(actions, start=1):
        action_path = actions_dir / f"{index:02d}-{slugify(action)}.md"
        action_path.write_text(
            action_prompt(args.pet_name, args.style, action, args.notes),
            encoding="utf-8",
        )
        action_prompt_paths[action] = str(action_path)

    request = {
        "pet_name": args.pet_name,
        "pet_id": slug,
        "style": args.style,
        "actions": actions,
        "notes": args.notes,
        "source_photo": str(photo),
        "reference_photo": str(photo_copy),
        "base_prompt": str(prompt_path),
        "action_prompts": action_prompt_paths,
        "run_dir": str(run_dir),
        "expected_pet_dir": str(codex_home() / "pets" / slug),
        "next_step": "Use $imagegen with base_prompt and reference_photo, then use action_prompts plus the canonical base to generate action images/rows before continuing with $hatch-pet to package the pet.",
    }
    request_path = run_dir / "photo-pet-request.json"
    request_path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(request, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
