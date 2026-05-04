# Photo To Codex Pet.skill

> *「把一张照片，孵成陪你工作的 Codex 桌宠。」*  
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
> [![Codex Skill](https://img.shields.io/badge/Codex-Skill-blueviolet)](SKILL.md)

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
