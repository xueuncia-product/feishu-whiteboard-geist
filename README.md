# feishu-whiteboard-geist

一个 **Claude Code skill**：把一段想法/内容，按 **Geist 绿白**工作图表规范，自动选合适的画板范式（全景 / 骨架 / 路线 / 机制），产出 SVG → 渲染回看修 → 推成一张**飞书可编辑画板**，最后给文档链接 + 渲染图。

这是工作型图表（汇报 / 脑暴 / 共创）的默认通道，强制走 Geist 绿白单一规范——不是 35 色板自由选择那套（那是 [`beautiful-feishu-whiteboard`](https://www.npmjs.com/package/@larksuite/cli)）。

## 是什么

“好看”的本质是约束：90% 中性灰阶 + 唯一一个绿做强调；边框优先于阴影；语义上色不是装饰上色。

| 内容形态 | 范式 |
|---|---|
| 一个体系的全貌、分层结构 | **全景图** |
| 讨论锚点、只到模块层 | **骨架图** |
| 阶段推进、分场流程 | **路线图** |
| 一个机制怎么运转 | **机制图** |

## 依赖

- [`lark-cli`](https://www.npmjs.com/package/@larksuite/cli)（npm `@larksuite/cli`）——已装且已登录
- `@larksuite/whiteboard-cli`（走 `npx` 自动下载，无需预装）
- 一个飞书 / Lark 账号

## 安装

Claude Code skill 装在 `~/.claude/skills/` 下。本 skill 正文会读两份规范文件，需放到它期望的位置：

```bash
git clone https://github.com/xueuncia-product/feishu-whiteboard-geist.git
cd feishu-whiteboard-geist

# 1. skill 本体
mkdir -p ~/.claude/skills/feishu-whiteboard-geist
cp SKILL.md ~/.claude/skills/feishu-whiteboard-geist/SKILL.md

# 2. Geist 设计规范（skill 正文引用 ~/.claude/diagram-visual-spec.md）
cp references/diagram-visual-spec.md ~/.claude/diagram-visual-spec.md

# 3. 飞书画板硬规则（skill 正文引用 beautiful-feishu-whiteboard/RULES.md）
mkdir -p ~/.claude/skills/beautiful-feishu-whiteboard
cp references/RULES.md ~/.claude/skills/beautiful-feishu-whiteboard/RULES.md
```

> SKILL.md 里用的是 `~/.claude/...` 绝对路径（为作者本机定制）。如果你的 skill 目录布局不同，按上面三个路径对应调整即可。

## 目录

```
SKILL.md                          # skill 本体
references/diagram-visual-spec.md # Geist 绿白调色板 + 视觉规范
references/RULES.md               # 飞书 SVG 画板硬限制 + 渲染/推送命令（来自上游 beautiful-feishu-whiteboard）
```

## 三条铁坑

1. **SVG 文字里禁 emoji**——whiteboard-cli 遇 emoji 会静默断图。
2. **导出 PNG 文字颜色不可信**（白字常变黑）——核验颜色看线上或用 `--output_as raw`。
3. **配色不要自由发挥**——只用 `diagram-visual-spec.md` 的 token。
