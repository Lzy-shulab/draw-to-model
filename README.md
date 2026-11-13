# DrawToModel

`draw-to-model` 是一个 Codex Skill，可把模型源码、算子草图或结构规格转成可编辑的 Draw.io 论文结构图。它沿 `forward` 梳理数据流，标注张量形状，并支持绘制注意力分支、跳连和消融对照。默认采用黑白版式。

[下载 ZIP](https://github.com/Lzy-shulab/draw-to-model/archive/refs/heads/main.zip)，解压后将包含 `SKILL.md` 的目录命名为 `draw-to-model`，放入本地 Codex 技能目录（例如 `~/.codex/skills/`）。然后在 Codex 中输入 `$draw-to-model`，并提供模型文件或结构说明。
