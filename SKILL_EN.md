---
name: feishu-whiteboard-geist
description: >
  The default "draw it on a Feishu whiteboard" flow. Invoke this skill when the ask is
  "draw this on a Feishu/Lark whiteboard / turn this into a whiteboard / draw a panorama
  (skeleton / roadmap / mechanism) diagram". It takes an idea or content, applies the Geist
  green-and-white work-diagram spec, auto-picks a fitting paradigm (panorama / skeleton /
  roadmap / mechanism), produces an SVG → render-review-fix → pushes it into an editable
  Feishu whiteboard, and returns the doc link + rendered image. This is the lane for
  work-style diagrams (reporting / brainstorming / co-creation) — NOT the free-choice
  35-palette flow (that is beautiful-feishu-whiteboard). This skill enforces the single
  Geist green-and-white spec and supports Feishu-editable output.
---

> This is an English rendering of `SKILL.md` for readers. The canonical, machine-loaded skill file is `SKILL.md`.

# Feishu Whiteboard · Geist Green-and-White (default flow)

"Draw this on a Feishu whiteboard" ≈ invoke this skill. Goal: **turn an idea into a single Geist green-and-white, good-looking, Feishu-editable work diagram.**

Good looks come from constraint: 90% neutral grays + one single green accent; borders over shadows; semantic coloring, not decorative coloring. Don't improvise colors, don't add effects.

## Dependencies (install first)
This skill is only the "Geist constraint layer". The actual draw/push engine is the standalone open-source skill **`beautiful-feishu-whiteboard`** (zarazhangrui) + `lark-cli`. See the repo README for install steps. Without the engine installed, this skill cannot push.

## Two required reads (read before you start — single source of truth, don't rely on memory)

1. **Design spec** `~/.claude/diagram-visual-spec.md` (repo `references/diagram-visual-spec.md`) — palette tokens, visual rules, the four paradigms, pitfalls. **All color and composition follow it.**
2. **Medium hard rules + commands** `~/.claude/skills/beautiful-feishu-whiteboard/RULES.md` (repo `references/RULES.md`) — the hard limits of Feishu SVG whiteboards + the exact render/write/verify commands. **Render and push commands follow it.**

> Relationship: this skill owns "pick the paradigm + enforce Geist + guarantee editability"; beautiful-feishu-whiteboard owns "medium hard rules + commands". Read both; color follows Geist only, not the 35-palette set.

## Step 0: Preflight
`lark-cli` (npm `@larksuite/cli`) installed and logged in; `@larksuite/whiteboard-cli` auto-downloads via npx. If not installed, tell the user how to install and stop (see the beautiful skill's preflight).

## Step 1: Pick the paradigm (this is a judgment step — don't skip)
First get clear on "what relationship is this content", then pick the diagram. **Ask yourself: what should this diagram make people see at a glance?**

| Content shape | Pick this paradigm | How to draw |
|---|---|---|
| The full view / layered structure of a system | **Panorama** | Layered layout (base → pillars → operations → endgame), color each block by four-tier status, put a green hard-data strip at the bottom |
| A discussion anchor, only down to the module level | **Skeleton** | A shallow map of hub (green) + trunks (category colors), **no detail** |
| Phased progression, scene-by-scene flow | **Roadmap** | Horizontal phase/scene card flow, neutral-dark at the ends, category colors in the middle, outputs tagged semantically |
| How a single mechanism works | **Mechanism** | Left-right / top-bottom contrast + marker arrows, emphasizing the operating logic |

If unsure, tell the user in one sentence which type you judged it to be and why; ask once before drawing if needed.

## Step 2: Draw → render → review-fix (the round that produces polish)
- SVG logical width ~1500–1700, **native shapes only** (rect/circle/line/text), **no font-family**.
- Colors from Geist tokens only; **one main accent per diagram** (green goes to the single most important point); color semantically/categorically per the spec's four tiers / five categories.
- Put only content on the board — **don't write instructions/sources/paradigm names/"summary…" onto the canvas** (that reads like a homework header; those go in the chat reply).
- Render: `whiteboard-cli -i x.svg -o x.png -f svg` → **review and fix** (overflow/alignment/margins/numbers hugging edges/half-images) → edit the SVG in place, batch one round of fixes then re-render — don't re-render on every single change, don't regenerate the whole thing.
- (Optional) recolor a ready-made linen board to Geist: `python3 scripts/recolor_geist.py <board>-linen.svg` (status/structure type) or `recolor_geist_cat.py` (categorical type).

## Step 3: Push to an editable Feishu whiteboard (must be editable, not a screenshot)
Follow the write commands in `references/RULES.md`: insert a `<whiteboard>` block in a Feishu doc → get the block_token → `whiteboard-cli --to openapi | lark-cli whiteboard +update --whiteboard-token <tok> --source - --input_format raw --overwrite --as user` to push the SVG.

To add a top board to an **existing** doc:
`lark-cli docs +update --doc <doc_tok> --command block_insert_after --block-id <full id of first block> --content '<whiteboard type="blank"></whiteboard>' --as user`
→ take the new block's `block_token` from the response → push the SVG with the `whiteboard +update` above. Mid-doc insert is the same, just point `--block-id` at the target paragraph block.
> ⚠️ `--block-id` must be the **full ID** (the long string from `GET /blocks`); a truncated one silently no-ops (returns ok but inserts nothing).

## Step 4: Deliver
Give the user **two things**: ① the Feishu doc/whiteboard link; ② the rendered image itself (so they can see it without opening the doc).

## Three hard pitfalls (always avoid)
1. **No emoji in SVG text** (⭐🚀🎯⚠️ etc.) — whiteboard-cli silently breaks the image on emoji, emitting half a board without error. Use color blocks / background tints / ①②③ circled numbers instead.
2. **Exported-PNG text color is unreliable** (white text often turns black) — verify colors online or use `--output_as raw`, don't trust the exported image.
3. **Don't improvise colors** — use only the tokens from `diagram-visual-spec.md`; every extra color makes it a bit uglier.
