---
name: feishu-whiteboard-geist
description: >
  薛张明的默认「用飞书画板画一下」流程。当他说「你用飞书画板画一下 / 用画板画 / 画成画板 / 把这段画出来 / 画个全景图(骨架图/路线图/机制图)」时调用本 skill。
  它把一段想法/内容，按 Geist 绿白工作图表规范，自动选合适的画板范式（全景/骨架/路线/机制），产出 SVG → 渲染回看修 → 推成「飞书可编辑画板」，最后给文档链接 + 渲染图。
  这是工作型图表（汇报/脑暴/共创）的默认通道——不是 35 色板自由选择那套（那是 beautiful-feishu-whiteboard）。本 skill 强制走 Geist 绿白单一规范并支持飞书可编辑。
---

# 飞书画板 · Geist 绿白（薛张明默认流程）

薛张明说「你用飞书画板画一下」≈ 调用本 skill。目标：**把想法变成一张 Geist 绿白、好看、且飞书内可编辑的工作图表。**

好看的本质是约束：90% 中性灰阶 + 唯一一个绿做强调；边框优先于阴影；语义上色不是装饰上色。别自由配色、别加特效。

## 依赖（必先装）
本 skill 只是「Geist 约束层」，真正的画图/推送引擎是独立开源 skill **`beautiful-feishu-whiteboard`**（zarazhangrui）+ `lark-cli`。安装详见仓库 README。未装引擎时，本 skill 无法推送。

## 必读两份（动手前读，单一来源，不要凭记忆）

1. **设计规范** `~/.claude/diagram-visual-spec.md`（本仓库 `references/diagram-visual-spec.md`）—— 调色板 token、视觉规则、四类范式、踩坑。**配色与构图一律按它。**
2. **介质硬规则 + 命令** `~/.claude/skills/beautiful-feishu-whiteboard/RULES.md`（本仓库 `references/RULES.md`）—— 飞书 SVG 画板的硬限制 + 渲染/写入/校验的确切命令。**渲染和推送命令以它为准。**

> 关系：本 skill 负责「选范式 + 守 Geist 规范 + 保证可编辑」；beautiful-feishu-whiteboard 负责「介质硬规则 + 命令」。两份都读，配色只走 Geist 不走 35 色板。

## 第 0 步：前置检查
`lark-cli`（npm `@larksuite/cli`）已装且已登录；`@larksuite/whiteboard-cli` 走 npx 自动下载。没装就先告诉他怎么装再停（见 beautiful skill 的 preflight）。

## 第 1 步：选范式（这步是判断，不要跳）
先想清楚「这内容是什么关系」，再选图。**先问自己一句：这张图要让人一眼看到什么？**

| 内容形态 | 选这个范式 | 怎么画 |
|---|---|---|
| 一个体系的全貌、分层结构 | **全景图** | 分层铺（地基→支柱→运营→终局），每块按四档状态上色，底部放绿色硬数据条 |
| 讨论锚点、只到模块层 | **骨架图** | 中枢(绿)+主干(分类色)的浅层导图，**不画细节** |
| 阶段推进、分场流程 | **路线图** | 横向阶段/分场卡片流，首尾中性深、中段分类色，产出用语义 tag |
| 一个机制怎么运转 | **机制图** | 左右/上下对照 + marker 箭头，突出运转逻辑 |

拿不准就用一句话告诉他你判断成哪类、为什么，必要时问一句再画。

## 第 2 步：作图 → 渲染 → 回看修（出精致度的关键一轮）
- SVG 逻辑宽 ~1500–1700，**只用原生形状**（rect/circle/line/text），**不设 font-family**。
- 颜色只用 Geist token；**一图一主强调**（绿色只给最重要那一个点）；语义/分类按规范四档/五类上色。
- 画板只放内容，**不要把指令/来源/范式名/“总结…”写到画布上**（那像作业抬头，那些放聊天回复里）。
- 渲染：`whiteboard-cli -i x.svg -o x.png -f svg` → **看图修**（溢出/对齐/边距/数字贴边/半张图）→ 就地小改 SVG、一轮批量改完再重渲，别每改一处重渲、别整张重生成。
- （可选）把现成的 linen 配色画板换成 Geist：`python3 scripts/recolor_geist.py <图>-linen.svg`（状态/结构型）或 `recolor_geist_cat.py`（分类型）。

## 第 3 步：推成飞书可编辑画板（必须可编辑，不是贴图）
按 `references/RULES.md` 的写入命令：在飞书 doc 里插 `<whiteboard>` 块 → 拿 block_token → `whiteboard-cli --to openapi | lark-cli whiteboard +update --whiteboard-token <tok> --source - --input_format raw --overwrite --as user` 推 SVG。

给**已有**文档加顶部画板：
`lark-cli docs +update --doc <doc_tok> --command block_insert_after --block-id <首块完整id> --content '<whiteboard type="blank"></whiteboard>' --as user`
→ 从返回里拿新块 `block_token` → 用上面的 `whiteboard +update` 推 SVG。中段插同理，`--block-id` 用目标段落块即可。
> ⚠️ `--block-id` 必须用**完整 ID**（`GET /blocks` 拿到的长串），截短的会静默 no-op（返回 ok 却什么都没插）。

## 第 4 步：交付
给他**两样**：① 飞书文档/画板链接；② 渲染图本身（方便不开文档就看）。

## 三条铁坑（一定避开）
1. **SVG 文字里禁 emoji**（⭐🚀🎯⚠️ 等）——whiteboard-cli 遇 emoji 会静默断图，只出半张还不报错。用色块/底色/①②③ 圈号替代。
2. **导出 PNG 文字颜色不可信**（白字常变黑）——核验颜色看线上或用 `--output_as raw`，别信导出图。
3. **配色不要自由发挥**——只用 `diagram-visual-spec.md` 的 token；多一个颜色就丑一分。
