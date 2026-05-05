# Photo To Codex Pet.skill

> *「把一张照片，孵成陪你工作的 Codex 桌宠。」*  
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
> [![Codex Skill](https://img.shields.io/badge/Codex-Skill-blueviolet)](SKILL.md)

**Language / 语言**: [中文](#中文说明) · [English](#english-version)

---

## 中文说明

**Photo To Codex Pet** 是一个 Codex skill：上传或指定一张人物照片，它会帮你生成卡通或写实风格的 Codex 桌宠，并自动准备动作、图集、配置文件和校验预览。

它不是只生成一张静态头像，而是面向桌宠使用场景，支持生成多个语义动作：

```text
办公、休息、思考、游戏、度假、开心、生气
```

[效果示例](#效果示例) · [安装](#安装) · [快速使用](#快速使用) · [工作原理](#工作原理) · [仓库结构](#仓库结构) · [FAQ](#faq)

---

## 效果示例

### 写实模式

适合希望尽量贴近原照片的人物桌宠。

```text
用户 ❯ 使用 $photo-to-codex-pet，把 ~/Pictures/me.jpg 做成写实风格 Codex 桌宠，
       名字叫 小明2号，pet-id 用 xiaoming2，
       动作包括 办公、休息、思考、游戏、度假、开心、生气。

Codex ❯ 已生成并配置：
       ~/.codex/pets/xiaoming2/pet.json
       ~/.codex/pets/xiaoming2/spritesheet.webp

       校验通过：1536x1872、WEBP、RGBA、无错误无警告。
```

写实模式会尽量保持：

- 脸型、发型、发量和分缝
- 眼镜形状、表情、肤色印象
- 衣服、颜色、西装纹理、领带
- 原照片里的整体姿态和气质

并明确避免：

- chibi 化
- 大眼睛化
- anime 化
- 换衣服
- 变成另一个 generic avatar

### 卡通模式

适合希望获得更“桌宠感”的可爱小人。

```text
用户 ❯ 使用 $photo-to-codex-pet，把 ~/Pictures/me.jpg 做成卡通风格 Codex 桌宠，
       名字叫 小明，pet-id 用 xiaoming。

Codex ❯ 已生成卡通桌宠形象，并打包到：
       ~/.codex/pets/xiaoming/
```

卡通模式会保留人物的高层识别特征，但整体会更像小型像素风/扁平风桌宠。

---

## 安装

### 方法一：让 Codex 从 GitHub 安装

在 Codex 里直接说：

```text
从 https://github.com/lingeringlight/photo-to-codex-pet 安装这个 Codex skill，
然后用它把我的照片做成桌宠。
```

### 方法二：手动 clone 到 skills 目录

```bash
git clone https://github.com/lingeringlight/photo-to-codex-pet.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/photo-to-codex-pet"
```

然后重启 Codex，或打开一个新线程让 skill 列表刷新。

### 方法三：如果你的环境支持 skills CLI

```bash
npx skills add lingeringlight/photo-to-codex-pet
```

---

## 快速使用

先把照片放到一个容易引用的位置，例如：

```text
~/Pictures/codex-pets/me.jpg
```

然后在 Codex 里说：

```text
使用 $photo-to-codex-pet，把 ~/Pictures/codex-pets/me.jpg 做成写实风格 Codex 桌宠，
名字叫 小明2号，pet-id 用 xiaoming2，
动作包括 办公、休息、思考、游戏、度假、开心、生气。
```

卡通版：

```text
使用 $photo-to-codex-pet，把 ~/Pictures/codex-pets/me.jpg 做成卡通风格 Codex 桌宠，
名字叫 小明，pet-id 用 xiaoming，
动作包括 办公、休息、思考、游戏、度假、开心、生气。
```

完成后，桌宠会被安装到：

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
  pet.json
  spritesheet.webp
```

如果桌宠选择面板里没有马上出现，重启 Codex App 或重新打开桌宠选择面板。

---

## 命令行准备

这个脚本会创建可复现的 run 目录，并生成 base prompt 与 action prompts。  
注意：它只是准备流程，不会单独完成图像生成；后续仍由 Codex 调用 `$imagegen` 和 `$hatch-pet`。

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/photo-to-codex-pet/scripts/start_photo_pet_run.py" \
  --photo /absolute/path/to/person-photo.jpg \
  --pet-name "小明2号" \
  --pet-id xiaoming2 \
  --style realistic \
  --actions "办公,休息,思考,游戏,度假,开心,生气" \
  --force
```

参数说明：

| 参数 | 作用 |
|---|---|
| `--photo` | 人物照片的绝对路径 |
| `--pet-name` | Codex 里显示的桌宠名字 |
| `--pet-id` | ASCII 包名和目录名，推荐必填 |
| `--style` | `cartoon` 或 `realistic` |
| `--actions` | 逗号分隔的动作列表 |
| `--force` | 覆盖已有 run 元数据 |

---

## 它生成了什么

运行目录：

```text
${CODEX_HOME:-$HOME/.codex}/pet-runs/<pet-id>/
  photo-pet-request.json
  references/
    person-reference.jpg
    canonical-base.png
  prompts/
    base-character.md
    actions/
      01-*.md
      02-*.md
      ...
```

安装目录：

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
  pet.json
  spritesheet.webp
  _conversion_qa/
    contact-sheet.png
    action-preview.png
    validation.json
```

Codex 桌宠最终识别的是：

```text
pet.json
spritesheet.webp
```

其中 `spritesheet.webp` 是标准 Codex 桌宠图集：

```text
1536 x 1872
8 列 x 9 行
每格 192 x 208
RGBA / 透明背景
```

---

## 工作原理

输入一张人物照片后，这个 skill 做四件事。

**1. 建立人物基准形象**

Codex 先读取照片，生成一个 `canonical-base`。  
卡通模式会桌宠化；写实模式会尽量贴近原照片。

**2. 生成语义动作**

默认生成：

| 动作 | 说明 |
|---|---|
| 办公 | 小电脑、文件或专注工作姿态 |
| 休息 | 放松、喝水、休息姿态 |
| 思考 | 托腮、皱眉、思考姿态 |
| 游戏 | 手柄、小型游戏动作 |
| 度假 | 放松、旅行氛围，但不生成大背景 |
| 开心 | 微笑、庆祝、挥手 |
| 生气 | 不满、皱眉、握拳，但不暴力 |

所有动作都遵守身份锁定：

- 同一张脸
- 同一发型
- 同一副眼镜
- 同一套衣服
- 同一整体轮廓

**3. 映射到 Codex 固定图集**

Codex 桌宠当前是固定 9 行 atlas。语义动作会被映射进去：

| Codex 行 | 使用动作 |
|---|---|
| `idle` | base / 开心 |
| `running-right` | 游戏或通用运动 |
| `running-left` | 镜像运动 |
| `waving` | 开心 |
| `jumping` | 度假或开心 |
| `failed` | 生气 |
| `waiting` | 休息 / 思考 |
| `running` | 游戏或通用运动 |
| `review` | 办公 / 思考 |

每一行都应该是动作序列，而不是把一张静态姿势复制多次。Codex 固定读取这些帧数：`idle` 6 帧、`running-right` 8 帧、`running-left` 8 帧、`waving` 4 帧、`jumping` 5 帧、`failed` 8 帧、`waiting` 6 帧、`running` 6 帧、`review` 6 帧。每个状态应在同一行内完成自然的小循环。

如果想把桌宠配置成“默认度假、鼠标悬停工作、完成后开心、运行中思考和办公轮换、拖动时撒娇、失败或偶发时累瘫”，按 Codex 当前硬编码事件映射：

| Codex 行 | 推荐语义 |
|---|---|
| `idle` | 度假 |
| `jumping` | 办公 / 工作，因为鼠标悬停触发这一行 |
| `review` | 开心，因为完成且有未读结果触发这一行 |
| `running` | 思考和办公在同一行内交替 |
| `running-right` | 向右拖动时撒娇 |
| `running-left` | 向左拖动时撒娇 |
| `failed` | 累瘫 |
| `waiting` | 思考 / 等待 |

新版本的准备脚本会自动把这个流程写进 run 目录：

```text
<run-dir>/
  codex-status-behavior-map.json
  prompts/
    base-character.md
    actions/
    codex-rows/
      idle.md
      running-right.md
      running-left.md
      waving.md
      jumping.md
      failed.md
      waiting.md
      running.md
      review.md
```

推荐执行顺序是：先用上传/本地照片生成完整自然的 `canonical-base.png`，再用 `prompts/codex-rows/*.md` 逐行生成真正的多帧动画条，最后交给 `hatch-pet` 组装、校验、预览和安装。不要用本地脚本拼身体，也不要把一张姿势复制成整行动画。

**4. 校验并安装**

最后生成 `pet.json` 和 `spritesheet.webp`，并用 Codex pet 校验脚本检查：

- 尺寸是否正确
- 未使用格子是否透明
- 背景是否透明
- atlas 是否可被 Codex 读取

---

## 仓库结构

```text
photo-to-codex-pet/
├── SKILL.md
├── README.md
├── LICENSE
├── agents/
│   └── openai.yaml
└── scripts/
    └── start_photo_pet_run.py
```

`SKILL.md` 是给 Codex 看的流程说明。  
`start_photo_pet_run.py` 是可复现的准备脚本。  
真正的图片生成和桌宠打包由 Codex 根据 skill 调用 `$imagegen` 和 `$hatch-pet` 完成。

---

## FAQ

### 为什么需要 `pet-id`？

中文名、空格和特殊字符不适合作为稳定目录名。推荐这样写：

```text
名字叫 小明2号，pet-id 用 xiaoming2
```

### 写实模式为什么还不是完全照片？

桌宠需要透明背景、全身图和小尺寸可读性。  
写实模式会尽量贴近照片，但仍会做少量桌宠化处理，避免生成结果在 `192x208` 小格子里糊成一团。

### 可以自定义动作吗？

可以：

```text
动作包括 读书、写代码、喝咖啡、开心、生气。
```

或命令行：

```bash
--actions "读书,写代码,喝咖啡,开心,生气"
```

### 生成出来还是有绿色背景怎么办？

让 Codex 重新执行抠绿背景和 atlas 校验：

```text
重新抠除绿色背景，并验证 spritesheet.webp 是否通过 Codex atlas 校验。
```

### 桌宠没有出现在 Codex 里怎么办？

确认目录里有：

```text
~/.codex/pets/<pet-id>/pet.json
~/.codex/pets/<pet-id>/spritesheet.webp
```

然后重启 Codex App。

---

## 许可证

MIT — 可以自由使用、修改和分享。

---

## English Version

# Photo To Codex Pet.skill

> *"Turn a photo into a Codex desktop pet that keeps you company while you work."*  
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
> [![Codex Skill](https://img.shields.io/badge/Codex-Skill-blueviolet)](SKILL.md)

**Photo To Codex Pet** is a Codex skill that turns a local or uploaded person photo into a configured Codex desktop pet. It can create either a cartoon pet or a photo-faithful realistic pet, prepare semantic actions, build the pet spritesheet, write configuration files, and generate validation previews.

It is not just a static avatar generator. It is designed for desktop-pet workflows and supports multiple semantic actions:

```text
working, resting, thinking, gaming, vacation, happy, angry
```

[Examples](#examples) · [Installation](#installation) · [Quick Start](#quick-start) · [How It Works](#how-it-works) · [Repository Structure](#repository-structure) · [FAQ](#faq-1)

---

## Examples

### Realistic Mode

Use this mode when you want the desktop pet to stay as close as possible to the original photo.

```text
User ❯ Use $photo-to-codex-pet to turn ~/Pictures/me.jpg into a realistic Codex desktop pet.
       Name it 小明2号, use pet-id xiaoming2,
       and include actions: working, resting, thinking, gaming, vacation, happy, angry.

Codex ❯ Generated and configured:
       ~/.codex/pets/xiaoming2/pet.json
       ~/.codex/pets/xiaoming2/spritesheet.webp

       Validation passed: 1536x1872, WEBP, RGBA, no errors or warnings.
```

Realistic mode tries to preserve:

- face shape, hairstyle, hair volume, and hair parting
- glasses shape, expression, and skin tone impression
- clothing, colors, suit texture, and tie
- overall posture and visual presence from the source photo

It explicitly avoids:

- chibi proportions
- oversized eyes
- anime redesign
- outfit changes
- turning the person into a generic avatar

### Cartoon Mode

Use this mode when you want a cuter, more desktop-pet-like character.

```text
User ❯ Use $photo-to-codex-pet to turn ~/Pictures/me.jpg into a cartoon Codex desktop pet.
       Name it 小明 and use pet-id xiaoming.

Codex ❯ Generated a cartoon desktop pet and packaged it under:
       ~/.codex/pets/xiaoming/
```

Cartoon mode preserves high-level identity cues while making the result feel more like a small pixel-adjacent or flat-shaded desktop companion.

---

## Installation

### Option 1: Ask Codex To Install From GitHub

In Codex, say:

```text
Install this Codex skill from https://github.com/lingeringlight/photo-to-codex-pet,
then use it to create a desktop pet from my photo.
```

### Option 2: Clone Into The Codex Skills Directory

```bash
git clone https://github.com/lingeringlight/photo-to-codex-pet.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/photo-to-codex-pet"
```

Then restart Codex, or open a new thread so the skill list refreshes.

### Option 3: If Your Environment Supports A Skills CLI

```bash
npx skills add lingeringlight/photo-to-codex-pet
```

---

## Quick Start

Put your photo somewhere easy to reference, for example:

```text
~/Pictures/codex-pets/me.jpg
```

Then ask Codex:

```text
Use $photo-to-codex-pet to turn ~/Pictures/codex-pets/me.jpg into a realistic Codex desktop pet.
Name it 小明2号, use pet-id xiaoming2,
and include actions: working, resting, thinking, gaming, vacation, happy, angry.
```

For cartoon style:

```text
Use $photo-to-codex-pet to turn ~/Pictures/codex-pets/me.jpg into a cartoon Codex desktop pet.
Name it 小明, use pet-id xiaoming,
and include actions: working, resting, thinking, gaming, vacation, happy, angry.
```

After completion, the pet is installed under:

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
  pet.json
  spritesheet.webp
```

If it does not appear immediately, restart the Codex app or reopen the desktop pet picker.

---

## Manual Preparation Command

This helper script creates a reproducible run folder and writes the base prompt plus action prompts. It does not generate the full pet by itself; Codex continues by calling `$imagegen` and `$hatch-pet`.

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/photo-to-codex-pet/scripts/start_photo_pet_run.py" \
  --photo /absolute/path/to/person-photo.jpg \
  --pet-name "小明2号" \
  --pet-id xiaoming2 \
  --style realistic \
  --actions "办公,休息,思考,游戏,度假,开心,生气" \
  --force
```

Arguments:

| Argument | Purpose |
|---|---|
| `--photo` | Absolute path to the person photo |
| `--pet-name` | Display name shown in Codex |
| `--pet-id` | Stable ASCII package and folder id, strongly recommended |
| `--style` | `cartoon` or `realistic` |
| `--actions` | Comma-separated action list |
| `--force` | Overwrite existing run metadata |

---

## What It Produces

Run folder:

```text
${CODEX_HOME:-$HOME/.codex}/pet-runs/<pet-id>/
  photo-pet-request.json
  references/
    person-reference.jpg
    canonical-base.png
  prompts/
    base-character.md
    actions/
      01-*.md
      02-*.md
      ...
```

Installed pet folder:

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
  pet.json
  spritesheet.webp
  _conversion_qa/
    contact-sheet.png
    action-preview.png
    validation.json
```

Codex recognizes the final pet from:

```text
pet.json
spritesheet.webp
```

The generated `spritesheet.webp` follows the standard Codex desktop pet atlas:

```text
1536 x 1872
8 columns x 9 rows
192 x 208 per cell
RGBA / transparent background
```

---

## How It Works

Given one person photo, this skill does four things.

**1. Builds a canonical character**

Codex reads the photo and generates a `canonical-base`. Cartoon mode stylizes it into a desktop pet. Realistic mode keeps it as close to the original photo as possible.

**2. Generates semantic actions**

Default actions:

| Action | Meaning |
|---|---|
| working | focused work pose with a small laptop or document |
| resting | relaxed pose, cup or rest gesture |
| thinking | chin-hand or focused thinking pose |
| gaming | small controller or playful gaming gesture |
| vacation | relaxed travel mood without a large background |
| happy | smile, celebration, or wave |
| angry | annoyed expression or clenched fists, nonviolent |

Every action keeps the identity locked:

- same face
- same hairstyle
- same glasses
- same outfit
- same overall silhouette

**3. Maps actions into Codex's fixed atlas**

Codex desktop pets currently use a fixed 9-row atlas. Semantic actions are mapped into those rows:

| Codex Row | Source Action |
|---|---|
| `idle` | base / happy |
| `running-right` | gaming or generic motion |
| `running-left` | mirrored motion |
| `waving` | happy |
| `jumping` | vacation or happy |
| `failed` | angry |
| `waiting` | resting / thinking |
| `running` | gaming or generic motion |
| `review` | working / thinking |

Each row should be a motion sequence, not one static pose copied into every frame. Codex reads these fixed frame counts: `idle` 6 frames, `running-right` 8, `running-left` 8, `waving` 4, `jumping` 5, `failed` 8, `waiting` 6, `running` 6, and `review` 6. Each state should complete a natural loop inside its own row.

For a behavior scheme like "vacation by default, work on hover, happy after completion, thinking/working while running, cute while dragging, exhausted on failures or occasional tired states", use Codex's current hardcoded event mapping:

| Codex Row | Recommended Meaning |
|---|---|
| `idle` | vacation |
| `jumping` | work / office, because hover triggers this row |
| `review` | happy, because completed unread work triggers this row |
| `running` | thinking and working alternating inside the same row |
| `running-right` | cute dragging-right loop |
| `running-left` | cute dragging-left loop |
| `failed` | exhausted / collapsed |
| `waiting` | thinking / waiting |

The preparation script now writes this flow directly into the run directory:

```text
<run-dir>/
  codex-status-behavior-map.json
  prompts/
    base-character.md
    actions/
    codex-rows/
      idle.md
      running-right.md
      running-left.md
      waving.md
      jumping.md
      failed.md
      waiting.md
      running.md
      review.md
```

The recommended order is: generate a coherent full-body `canonical-base.png` from the uploaded/local photo, generate each real multi-frame animation strip from `prompts/codex-rows/*.md`, then let `hatch-pet` assemble, validate, preview, and install the pet. Do not locally paste a body onto a photo head, and do not copy one pose across an entire animation row.

**4. Validates and installs**

The skill writes `pet.json` and `spritesheet.webp`, then validates:

- atlas dimensions
- transparent unused cells
- transparent background
- Codex-readable atlas format

---

## Repository Structure

```text
photo-to-codex-pet/
├── SKILL.md
├── README.md
├── LICENSE
├── agents/
│   └── openai.yaml
└── scripts/
    └── start_photo_pet_run.py
```

`SKILL.md` is the workflow guide for Codex.  
`start_photo_pet_run.py` is the reproducible preparation script.  
Image generation and pet packaging are handled by Codex through `$imagegen` and `$hatch-pet`.

---

## FAQ

### Why do I need `pet-id`?

Chinese names, spaces, and special characters are not ideal as stable folder names. Use:

```text
name it 小明2号, use pet-id xiaoming2
```

### Why is realistic mode not a perfect photo cutout?

A desktop pet needs a transparent background, a full-body sprite, and small-size readability. Realistic mode tries to stay close to the photo, but still adapts the result slightly so it works inside a `192x208` pet cell.

### Can I customize actions?

Yes:

```text
include actions: reading, coding, drinking coffee, happy, angry.
```

Or from the command line:

```bash
--actions "reading,coding,drinking coffee,happy,angry"
```

### The generated pet still has a green background. What should I do?

Ask Codex:

```text
Remove the green chroma-key background again and validate that spritesheet.webp passes the Codex atlas check.
```

### The pet does not appear in Codex. What should I check?

Make sure these files exist:

```text
~/.codex/pets/<pet-id>/pet.json
~/.codex/pets/<pet-id>/spritesheet.webp
```

Then restart the Codex app.

---

## License

MIT — free to use, modify, and share.
