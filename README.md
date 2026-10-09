**[English](README_EN.md) | 中文**

# feishu-whiteboard-geist

一个 **Claude Code skill**：把一段想法/内容，按 **Geist 绿白**工作图表规范，自动选合适的画板范式，产出 SVG → 渲染回看修 → 推成一张**飞书可编辑画板**，最后给文档链接 + 渲染图。

这是工作型图表（汇报 / 脑暴 / 共创）的默认通道，强制走 Geist 绿白单一规范——不是 35 色板自由选择那套。

## 架构：两层

- **引擎层 = [`beautiful-feishu-whiteboard`](https://github.com/zarazhangrui/beautiful-feishu-whiteboard)**（zarazhangrui 的独立开源 skill）：负责飞书 SVG 画板的介质硬规则 + 渲染/推送命令。
- **约束层 = 本 skill**：在引擎之上加一层 **Geist 绿白**规范 + 范式选择，让产出的是克制、好看、一致的工作图表。

> 本 skill **不能单独跑**，必须先装引擎 skill + `lark-cli`。

## 能画成什么样（示例 · 全虚构脱敏）

下面四张都是本 skill 按 Geist 规范生成的工作板，**数据、产品名、人名全部虚构脱敏**，仅展示密度与版式水准（SVG 源文件在 [`assets/`](assets)）。

### 架构全景 — 多业务线 × 分层平台
分层铺（业务层 → 功能模块层 → 共用底座 → 能力层 → 数据层），按业务线分类色 + owner 副标 + 密集 bullet 卡，待建项用琥珀 tag。

<img src="assets/board-architecture.svg" width="900" alt="架构全景示意"/>

### 数据分析板 — 趋势 / 漏斗 / 前后对比
柱状图（峰值描重、MTD 用琥珀虚线）+ 改版前后大数字对比 + 多级下钻漏斗 + 沉默占比大数字 + 底部数据条。

<img src="assets/board-data.svg" width="900" alt="数据分析板示意"/>

### 信息周报 — 情绪基调 / 信号 / 排序 / 建议
情绪基调三档语义卡 + 四大信号（顶部色条 + 来源）+ 竞品盯防排序 + 建议速览绿框。

<img src="assets/board-weekly.svg" width="900" alt="信息周报示意"/>

### 双坐标分层 — 9 宫格热力 + 决策点
9 宫格热力图（底色深浅 = 体量）+ 离群档琥珀虚线 + 两个权益域 + 越级 band + 底部 6 个待拍板决策卡。

<img src="assets/board-matrix.svg" width="900" alt="双坐标分层示意"/>

## 能画哪些图

skill 先判断「读者要看懂的是什么」（状态 / 交接 / 归因 / 取舍 / 依赖 / 情绪），再从下面选型：

| 内容形态 | 范式 |
|---|---|
| 一个体系的全貌、分层结构 | **全景图** |
| 讨论锚点、只到模块层 | **骨架图** |
| 阶段推进、分场流程 | **路线图** |
| 一个机制怎么运转 | **机制图** |
| 有数据要量化：对比 / 占比 / 趋势 / 流量 | **定量图表**（柱+折线 / 仪表盘 / 雷达 / 桑基 / 堆叠面积） |
| 状态流转、跨角色交接、分期、归因等 | **扩展 10 种**：状态机 · 泳道 · 故事地图 · 鱼骨 · 象限 · 依赖图 · 甘特 · 漏斗 · 时间轴 · 用户旅程 |
| 增减拆解、调用先后、闭环、系统改动、表关联、找异常、两时点对比、目标差距 | **扩展第二批 8 种**：瀑布 · 时序 · 飞轮 · 架构前后对比 · ER · 热力 · 斜率 · 哑铃 |

扩展 18 种的画法和连线规则（直角连线、端点离角 ≥ 8px、线上标签垫底色、图例放底部）改编自 [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)（MIT），已换成 Geist 绿白 + 飞书画板硬限制。

**第二批 8 种的样张**（源码 `scripts/pattern_examples.py`，一图一个函数，复制改数据即可）：

<p>
<img src="assets/patterns/01_waterfall.svg" width="440" alt="瀑布图"/> <img src="assets/patterns/02_sequence.svg" width="440" alt="时序图"/>
<img src="assets/patterns/03_flywheel.svg" width="440" alt="闭环飞轮"/> <img src="assets/patterns/04_arch_delta.svg" width="440" alt="架构前后对比"/>
<img src="assets/patterns/05_er.svg" width="440" alt="ER 图"/> <img src="assets/patterns/06_heatmap.svg" width="440" alt="热力图"/>
<img src="assets/patterns/07_slope.svg" width="440" alt="斜率图"/> <img src="assets/patterns/08_dumbbell.svg" width="440" alt="哑铃图"/>
</p>

## 依赖

1. **引擎 skill**：[`beautiful-feishu-whiteboard`](https://github.com/zarazhangrui/beautiful-feishu-whiteboard)（装到 `~/.claude/skills/`）
2. [`lark-cli`](https://www.npmjs.com/package/@larksuite/cli)（npm `@larksuite/cli`）——已装且已登录
3. `@larksuite/whiteboard-cli`（走 `npx` 自动下载，无需预装）
4. 一个飞书 / Lark 账号

## 安装

```bash
# 0. 先装引擎 skill（如已装可跳过）
git clone https://github.com/zarazhangrui/beautiful-feishu-whiteboard.git \
  ~/.claude/skills/beautiful-feishu-whiteboard

# 1. 整个仓库直接克隆成 skill 目录
git clone https://github.com/xueuncia-product/feishu-whiteboard-geist.git \
  ~/.claude/skills/feishu-whiteboard-geist
```

装完在 Claude Code 里说「用飞书画板画一下 xxx」即可触发。SKILL.md 引用的规范、脚本都用仓库内相对路径，无需再拷文件。

**更新**：`cd ~/.claude/skills/feishu-whiteboard-geist && git pull`

## 目录

```
SKILL.md                          # skill 本体
references/diagram-visual-spec.md # Geist 绿白调色板 + 视觉规范（自包含）
references/RULES.md               # 飞书 SVG 画板硬限制 + 渲染/推送命令（引擎 skill RULES.md 的副本）
references/patterns.md            # 扩展 18 种范式 + 连线规则：选型、画法、上限、反模式
references/quant-charts.md        # 定量图表选型与用法
scripts/geist_layout.py           # 复合信息板布局库（卡片/表格/KPI 条，字号钳制已内建）
scripts/quant_charts.py           # 5 类定量图表生成器
scripts/check_fonts.py            # 推送前硬闸：字号 < 13px 或非整数即报错
scripts/check_geometry.py         # 推送前硬闸：连线贴角 / 穿卡 / 贴边 / 重叠 / 标签没垫底
scripts/pattern_examples.py       # 第二批 8 种范式的示例生成器（一图一个函数）
scripts/recolor_geist.py          # 状态/结构型换肤：linen 配色 → Geist
scripts/recolor_geist_cat.py      # 分类型换肤
assets/                           # 4 张示例工作板 SVG + patterns/ 下 8 张范式样张（全虚构）
```

## 四条铁坑

1. **SVG 文字里禁 emoji**——whiteboard-cli 遇 emoji 会静默断图。
2. **导出 PNG 文字颜色不可信**（白字常变黑）——核验颜色看线上或用 `--output_as raw`。
3. **字号 < 13px 会在飞书线上折行**，本地渲染查不出——推前跑 `scripts/check_fonts.py` 和 `scripts/check_geometry.py`，推后看线上图。
4. **配色不要自由发挥**——只用 `diagram-visual-spec.md` 的 token。

## 致谢

引擎层基于 [zarazhangrui/beautiful-feishu-whiteboard](https://github.com/zarazhangrui/beautiful-feishu-whiteboard)。本仓只是在其上加一层 Geist 绿白约束。
