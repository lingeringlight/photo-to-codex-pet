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
            "Photo-faithful realistic Codex desktop pet mode. Use the source photo as the identity "
            "reference to create one coherent full-body realistic portrait/avatar, not a pasted "
            "collage. Match face shape, hairstyle, bangs, hair length, expression, skin tone "
            "impression, outfit style, colors, posture, and clothing details as closely as possible. "
            "If the photo is a headshot or ID photo, infer the missing lower body from the visible "
            "outfit so the whole character looks unified in lighting, scale, camera language, and "
            "material. Do not chibi-fy, do not enlarge the eyes, do not convert to anime, do not "
            "paste a photo head onto a mismatched drawn body, and do not invent a different outfit. "
            "Only simplify enough for a readable transparent desktop pet sprite."
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
    "撒娇": {
        "english": "cute pleading",
        "pose": "cute pleading pose with shy body sway, softened expression, small hand gesture close to the body",
        "avoid": "hearts, speech bubbles, detached sparkles, oversized props, room scenery",
    },
    "累瘫": {
        "english": "exhausted collapsed",
        "pose": "exhausted collapsed or slumped pose, tired expression, body lowered naturally but still fully visible",
        "avoid": "beds, large furniture, detached sleep symbols, injury, medical props, room scenery",
    },
}


CODEX_ROWS = [
    ("idle", 6),
    ("running-right", 8),
    ("running-left", 8),
    ("waving", 4),
    ("jumping", 5),
    ("failed", 8),
    ("waiting", 6),
    ("running", 6),
    ("review", 6),
]


DEFAULT_EVENT_BEHAVIOR = {
    "idle": {
        "event": "normal/default pet state",
        "action": "度假",
        "motion": "relaxed vacation breathing loop with subtle head, hand, and body shifts",
        "beats": [
            "relaxed vacation stance",
            "small smile and blink",
            "tiny hand or cup adjustment",
            "gentle shoulder shift",
            "returns toward relaxed stance",
            "settles into loop start",
        ],
    },
    "running-right": {
        "event": "dragging toward the right",
        "action": "撒娇",
        "motion": "cute pleading drag-right loop with real rightward limb and body motion",
        "beats": [
            "leans right shyly",
            "right foot steps",
            "hands close to chest",
            "small pleading look",
            "body sways right",
            "recovers balance",
            "another small step",
            "returns toward loop start",
        ],
    },
    "running-left": {
        "event": "dragging toward the left",
        "action": "撒娇",
        "motion": "cute pleading drag-left loop with real leftward limb and body motion",
        "beats": [
            "leans left shyly",
            "left foot steps",
            "hands close to chest",
            "small pleading look",
            "body sways left",
            "recovers balance",
            "another small step",
            "returns toward loop start",
        ],
    },
    "waving": {
        "event": "optional greeting row",
        "action": "撒娇",
        "motion": "short cute greeting loop with hand gesture only",
        "beats": [
            "hands close to body",
            "small shy hand lift",
            "gentle cute gesture",
            "hand returns",
        ],
    },
    "jumping": {
        "event": "pointer hover over the mascot",
        "action": "办公",
        "motion": "hover-triggered work loop with small laptop or document, not a literal jump",
        "beats": [
            "notices work",
            "leans to small laptop or document",
            "taps or writes",
            "focused look",
            "settles back to work stance",
        ],
    },
    "failed": {
        "event": "failed or blocked task",
        "action": "累瘫",
        "motion": "exhausted collapse loop with slumping, tired breathing, and partial recovery",
        "beats": [
            "tired upright pose",
            "shoulders drop",
            "knees bend or body lowers",
            "slumps down naturally",
            "tired blink",
            "small recovery breath",
            "still exhausted",
            "settles collapsed",
        ],
    },
    "waiting": {
        "event": "waiting for user input",
        "action": "思考",
        "motion": "waiting/thinking loop with hand near chin, glance, blink, and return",
        "beats": [
            "hand near chin",
            "slight head tilt",
            "glance aside",
            "blink",
            "thoughtful pause",
            "returns to first pose",
        ],
    },
    "running": {
        "event": "active/running task",
        "action": "思考和办公轮换",
        "motion": "active-task loop alternating thinking and working inside one row",
        "beats": [
            "thinking hand near chin",
            "leans toward small laptop or document",
            "working gesture",
            "pauses and thinks again",
            "returns to working",
            "settles back toward frame 1",
        ],
    },
    "review": {
        "event": "completed task with unread result",
        "action": "开心",
        "motion": "completion loop with smile, small celebration, and happy settle",
        "beats": [
            "notices completion",
            "smile grows",
            "small celebratory arm lift",
            "happy bounce or posture lift",
            "relaxes into smile",
            "returns toward loop start",
        ],
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


def row_prompt(name: str, style: str, row: str, frames: int, behavior: dict[str, object], notes: str) -> str:
    action = str(behavior["action"])
    spec = ACTION_SPECS.get(
        action,
        {
            "english": action,
            "pose": f"clear {action} themed pose",
            "avoid": "text, scenery, detached decorative symbols, large props",
        },
    )
    beats = behavior.get("beats", [])
    if not isinstance(beats, list) or len(beats) != frames:
        beats = [f"frame {index + 1}: continue the {action} loop" for index in range(frames)]
    beat_lines = "\n".join(f"- Frame {index + 1}: {beat}" for index, beat in enumerate(beats))
    identity_lock = (
        "Preserve the same person identity from the original photo and canonical full-body base: face shape, "
        "hairstyle, glasses, expression family, clothing, colors, natural proportions, and silhouette. "
        "Every frame must look like the same person and the same outfit."
        if style == "realistic"
        else "Preserve the same stylized character identity from the original photo and canonical base: hairstyle, glasses if present, outfit colors, face impression, proportions, and silhouette."
    )
    return f"""Use case: stylized-concept
Asset type: Codex desktop pet animation row strip
Primary request: Generate the `{row}` row for the pet named {name}.
Codex event: {behavior['event']}.
Semantic action: {action} / {spec['english']}.
Required frame count: {frames} separate full-body frames in one horizontal strip.
Identity lock: {identity_lock}
Motion design: {behavior['motion']}.
Frame beats:
{beat_lines}
Style notes: {style_notes(style)}
User notes: {notes or "None."}
Composition: one horizontal row strip with exactly {frames} evenly spaced full-body frames, generous padding in every frame, consistent scale and camera angle. Keep any prop small, held by or touching the character, and inside the frame.
Animation rule: do not copy one static pose across frames. Each used frame must show visible, coherent body/limb/expression change and the final frame must loop naturally back toward frame 1.
Background: perfectly flat solid #00ff00 chroma-key background for background removal. No shadows, gradients, scenery, floor plane, or lighting variation. Do not use #00ff00 anywhere in the subject.
Avoid: {spec['avoid']}; no watermark, no logo, no text, no frame numbers, no grid lines, no UI, no separate backgrounds, no local collage look, no pasted photo head, no mismatched body.
"""


def base_prompt(name: str, style: str, notes: str) -> str:
    mode = "photo-faithful realistic desktop pet cutout/avatar" if style == "realistic" else "cartoon chibi desktop pet"
    if style == "realistic":
        subject = (
            "Photo-faithful realistic full-body desktop pet character based directly on the reference "
            "person photo. Maximize likeness and photo fidelity, but make the output a single coherent "
            "full-body portrait/avatar rather than a cut-and-paste composite. Match the visible face "
            "shape, hairstyle, bangs, hair volume and parting, expression, skin tone impression, clothing, "
            "colors, suit texture, tie or bow, and overall posture. If the photo is a headshot, ID photo, "
            "or half-body portrait, infer the missing lower body from the visible outfit so the full body "
            "looks natural, unified, and plausible in the same lighting and style. Do not identify the "
            "person or add text."
        )
        avoid = (
            "no text, no watermark, no logo, no scenery, no cast shadow, no detached decorative effects, "
            "no chibi proportions, no oversized eyes, no anime redesign, no different outfit, no pasted-photo "
            "head, no mismatched drawn body, no visible seam, no glossy 3D render."
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
Composition: one complete character centered, front-facing 3/4 pose, generous padding, no cropping. In realistic mode, the whole character must look coherent like one generated/edited photo or realistic avatar, not a local collage.
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

    behavior_map_path = run_dir / "codex-status-behavior-map.json"
    behavior_map = {
        "codex_event_mapping": {
            row: {
                "event": DEFAULT_EVENT_BEHAVIOR[row]["event"],
                "semantic_action": DEFAULT_EVENT_BEHAVIOR[row]["action"],
                "frames": frames,
                "motion": DEFAULT_EVENT_BEHAVIOR[row]["motion"],
            }
            for row, frames in CODEX_ROWS
        },
        "implementation_rule": (
            "Generate the canonical full-body base from the photo first, then generate each fixed Codex row as "
            "a real multi-frame animation strip grounded by both the original photo and canonical base. Do not "
            "create missing body parts by local collage, and do not copy one static pose across row frames."
        ),
    }
    behavior_map_path.write_text(json.dumps(behavior_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    row_prompt_paths: dict[str, str] = {}
    row_prompts_dir = prompts / "codex-rows"
    row_prompts_dir.mkdir(parents=True, exist_ok=True)
    for row, frames in CODEX_ROWS:
        row_path = row_prompts_dir / f"{row}.md"
        row_path.write_text(
            row_prompt(args.pet_name, args.style, row, frames, DEFAULT_EVENT_BEHAVIOR[row], args.notes),
            encoding="utf-8",
        )
        row_prompt_paths[row] = str(row_path)

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
        "codex_status_behavior_map": str(behavior_map_path),
        "codex_row_prompts": row_prompt_paths,
        "run_dir": str(run_dir),
        "expected_pet_dir": str(codex_home() / "pets" / slug),
        "next_step": "Use $imagegen with base_prompt and reference_photo to create the canonical full-body base. Then use codex_row_prompts with the original photo plus canonical base to generate true multi-frame row strips, and continue with $hatch-pet to assemble, validate, and install the pet.",
    }
    request_path = run_dir / "photo-pet-request.json"
    request_path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(request, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
