# -*- coding: utf-8 -*-
"""Geist 绿白画板 · 复合信息板布局库

为什么需要它：飞书线上用 Noto Sans SC 渲染、字号有下限且会取整，而 whiteboard-cli
本地按自己的字体度量算文本节点宽度。二者不一致 → 线上文字折行、断下来的字压住下一行；
而**本地 PNG 与 `--check` 都发现不了**（它们与 whiteboard-cli 共用同一套度量）。

本库把三条防线固化进 helper，避免每张板重新踩：
  1. T()      —— 字号一律钳到 >= 13 且取整，杜绝线上折行的主因
  2. fit()    —— 按容器宽自适应缩字号，但下限同样是 13（低于 13 不是"缩小"，是"会折行"）
  3. strip()  —— 底部结论条一行放不下自动折两行，字号保持 14 不缩水

用法：
    import sys; sys.path.insert(0, "<此 skill>/scripts")
    from geist_layout import *
    p = []
    head(p, "标题", "右上角副信息")
    card(p, 40, 108, 800, 300, "分区标题", "green")
    strip(p, 760, "底部结论条")
    save(p, "board.svg", 820)

推送前务必：`python3 check_fonts.py board.svg` → 推线上 → 逐张 `whiteboard +query` 看线上图。
"""
"""六张 Geist 绿白画板：复刻原四图版式 + 两张新增。"""
import json, os
R = ""
OUT = ""   # 由调用方设置输出目录
G = dict(page="#FAFBFB", card="#FFFFFF", bd="#E1E3E4", grid="#EEF0F0", ink="#0A0C0C",
         body="#1A1E1F", muted="#6B7173", green="#10A37F", green_dk="#0B7355", green_lt="#E7F6F0",
         blue="#3B7DE0", blue_dk="#2C5FB0", blue_lt="#E9F1FC", amber="#E8A23D", amber_dk="#8A5B12",
         amber_lt="#FCF2E1", purple="#7E57C2", purple_lt="#F0ECF9", red="#D9534F", red_lt="#FBE9E7")
ST = {"green": (G["green_lt"], G["green"], G["green_dk"]),
      "amber": (G["amber_lt"], G["amber"], G["amber_dk"]),
      "red":   (G["red_lt"], G["red"], "#A23A33"),
      "blue":  (G["blue_lt"], G["blue"], G["blue_dk"]),
      "gray":  (G["page"], G["bd"], G["muted"])}
W = 1680

def T(x, y, s, size=14, fill=None, w="normal", anchor="start"):
    # 飞书线上正文有最小字号且会取整，<13px 的文字节点会被撑破而折行——统一钳到 13
    size = int(max(size, 13))
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" '
            f'fill="{fill or G["body"]}" text-anchor="{anchor}">{s}</text>')
def RECT(x, y, w, h, fill, stroke=None, rx=0, sw=2):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
    if stroke: s += f' stroke="{stroke}" stroke-width="{sw}"'
    return s + '/>'
def LINE(x1, y1, x2, y2, c, w=1):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"/>'

def _units(s):
    """粗估文本宽度（以 em 为单位）：CJK 与全角标点 1.0，拉丁 0.56。"""
    u = 0.0
    for ch in s:
        u += 1.0 if (ord(ch) > 0x2E80 or ch in "，。、；：（）「」·—～") else 0.56
    return u
def fit(x, y, s, maxw, size=15, fill=None, w="normal", anchor="start"):
    """按可用宽度自动缩字号，保证不溢出容器。"""
    sz = min(size, maxw / max(_units(s), 0.1))
    return T(x, y, s, int(max(sz, 13)), fill, w, anchor)

def head(p, title, right, h=60, y=28):
    p.append(RECT(40, y, W - 80, h, G["green"], rx=6))
    p.append(T(64, y + h / 2 + 10, title, 28, "#FFFFFF", "700"))
    p.append(T(W - 64, y + h / 2 + 8, right, 15, G["green_lt"], anchor="end"))
def strip(p, y, text):
    """底部结论条：一行放不下就自动折成两行，字号保持可读。"""
    avail = W - 128
    per = avail / 14.0 * 0.88          # 每行可容纳的 em 数（含安全余量）
    if _units(text) <= per:
        p.append(RECT(40, y, W - 80, 58, G["green"], rx=6))
        p.append(T(64, y + 36, text, 14, "#FFFFFF", "700"))
        return
    for mk in ["③", "④", "②"]:
        k = text.find(mk)
        if k > 0 and _units(text[:k]) <= per and _units(text[k:]) <= per:
            p.append(RECT(40, y, W - 80, 58, G["green"], rx=6))
            p.append(T(64, y + 24, text[:k].rstrip(), 14, "#FFFFFF", "700"))
            p.append(T(64, y + 46, text[k:], 14, "#FFFFFF", "700"))
            return
    seps = ["  |  ", "；", "，", " "]
    best = None
    for sp in seps:
        parts = text.split(sp)
        if len(parts) < 2: continue
        for k in range(1, len(parts)):
            a = sp.join(parts[:k]); b = sp.join(parts[k:])
            if sp == "  |  ": a += "  |"
            score = abs(_units(a) - _units(b))
            if max(_units(a), _units(b)) <= per and (best is None or score < best[0]):
                best = (score, a, b)
        if best: break
    if best is None:
        cut = int(len(text) * per / _units(text))
        best = (0, text[:cut], text[cut:])
    p.append(RECT(40, y, W - 80, 58, G["green"], rx=6))
    p.append(T(64, y + 24, best[1], 14, "#FFFFFF", "700"))
    p.append(T(64, y + 46, best[2], 14, "#FFFFFF", "700"))
def card(p, x, y, w, h, title, status="gray"):
    bg, bd, fg = ST[status]
    p.append(RECT(x, y, w, h, G["card"], G["bd"], rx=8))
    p.append(RECT(x, y, 6, h, bd, rx=3))
    if title: p.append(T(x + 22, y + 32, title, 18, G["ink"], "700"))
    return bd, fg
def save(p, name, h):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">'
           + RECT(0, 0, W, h, G["page"]) + "".join(p) + '</svg>')
    open(OUT + name, "w", encoding="utf-8").write(svg)
    print("wrote", name, len(svg))

