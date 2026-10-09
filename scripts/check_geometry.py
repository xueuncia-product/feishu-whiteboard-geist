# -*- coding: utf-8 -*-
"""画板连线几何检查（推送前跑，和 check_fonts.py 一起当硬闸）。

用法：python3 check_geometry.py a.svg [b.svg ...]   有 ERROR 退出码 1。

只看带 marker-end 的 <line>/<polyline>（即会变成原生连接器的线），节点是带描边、≥60×40 的 <rect>
（套着别的节点的大面板算容器，不当节点）。规则改编自 cathrynlavery/diagram-design 的
verify-geometry.py（MIT），按飞书画板只有直线/直角线的情况裁剪：
  ERROR  端点贴在节点角上 8px 以内          → 连接器会从角上斜出去，挪到边的中段
  ERROR  线段穿过不相干的节点               → 线被卡片压住或压住卡片，改走直角绕开
  ERROR  线段贴着节点边框跑                 → 线和边框叠成一条，看不出连到哪
  WARN   两条连接器重叠一段                 → 读不出是两条线，错开 ≥12px
  WARN   斜线段                             → 画板只认直线/直角；飞轮这种有意斜连可忽略
  WARN   文字压在连接器上且底下没有不透明垫底 → 用垫底色的标签（masklabel）
文字宽度按 geist_layout._units 估，和布局库同一套。
"""
import math, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geist_layout import _units

CORNER = 8.0      # 端点离节点角的最小距离
ATTACH = 14.0     # 端点离节点边多近算"连在它上面"（箭头通常停在边外 6px）
RIDE = 4.0        # 贴边容差
OVERLAP = 8.0     # 两条线共线重叠多长算重叠

def _attrs(s):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', s))

def _num(a, k, d=0.0):
    try: return float(a.get(k, d))
    except ValueError: return d

def parse(src):
    nodes, conns, rects, texts = [], [], [], []
    for m in re.finditer(r'<(rect|line|polyline|text)\b([^>]*)>', src):
        tag, a, pos = m.group(1), _attrs(m.group(2)), m.start()
        if tag == "rect":
            x, y, w, h = (_num(a, k) for k in ("x", "y", "width", "height"))
            filled = a.get("fill", "#000") not in ("none", "transparent")
            rects.append((pos, x, y, w, h, filled))
            if a.get("stroke", "none") != "none" and w >= 60 and h >= 40:
                nodes.append((x, y, w, h))
        elif tag in ("line", "polyline") and "marker-end" in a:
            if tag == "line":
                pts = [(_num(a, "x1"), _num(a, "y1")), (_num(a, "x2"), _num(a, "y2"))]
            else:
                v = [float(t) for t in re.split(r"[\s,]+", a.get("points", "").strip()) if t]
                pts = list(zip(v[0::2], v[1::2]))
            if len(pts) >= 2:
                conns.append((pos, f"连接器#{len(conns) + 1}({pts[0][0]:g},{pts[0][1]:g})", pts))
        elif tag == "text":
            end = src.find("</text>", m.end())
            s = re.sub(r"<[^>]+>", "", src[m.end():end])
            size = _num(a, "font-size", 14)
            w = _units(s) * size
            x = _num(a, "x")
            x -= {"middle": w / 2, "end": w}.get(a.get("text-anchor", "start"), 0)
            texts.append((pos, "文字", s, x, _num(a, "y") - size * 0.8, w, size))
    # 套着别的节点的是容器面板，不参与节点判定
    def inside(i, o):
        return i != o and o[0] <= i[0] and o[1] <= i[1] and i[0] + i[2] <= o[0] + o[2] and i[1] + i[3] <= o[1] + o[3]
    nodes = [n for n in nodes if not any(inside(o, n) for o in nodes)]
    return nodes, conns, rects, texts

def seg_hits_box(p, q, x0, y0, x1, y1):
    """Liang–Barsky：线段是否穿过矩形内部。"""
    (px, py), (qx, qy) = p, q
    dx, dy, t0, t1 = qx - px, qy - py, 0.0, 1.0
    for pp, qq in ((-dx, px - x0), (dx, x1 - px), (-dy, py - y0), (dy, y1 - py)):
        if pp == 0:
            if qq < 0: return False
        else:
            t = qq / pp
            if pp < 0: t0 = max(t0, t)
            else: t1 = min(t1, t)
            if t0 > t1: return False
    return t1 - t0 > 1e-6

def near_node(pt, n, tol):
    x, y, w, h = n
    return x - tol <= pt[0] <= x + w + tol and y - tol <= pt[1] <= y + h + tol

def check(path):
    src = open(path, encoding="utf-8").read()
    nodes, conns, rects, texts = parse(src)
    out = []
    segs_all = []
    for pos, ln, pts in conns:
        ends = [pts[0], pts[-1]]
        owners = [n for n in nodes if any(near_node(e, n, ATTACH) and not near_node(e, n, -2) for e in ends)]
        for e in ends:
            for x, y, w, h in owners:
                if not near_node(e, (x, y, w, h), ATTACH): continue
                # 先判端点连在哪条边，再量它沿这条边离两端角多远
                dh = min(abs(e[1] - y), abs(e[1] - y - h))   # 到上/下边
                dv = min(abs(e[0] - x), abs(e[0] - x - w))   # 到左/右边
                along = min(abs(e[0] - x), abs(e[0] - x - w)) if dh <= dv else min(abs(e[1] - y), abs(e[1] - y - h))
                if along < CORNER:
                    out.append(("ERROR", ln, f"端点 {e[0]:g},{e[1]:g} 离节点 {x:g},{y:g} 的角不到 {CORNER:g}px，挪到边的中段"))
        for p, q in zip(pts, pts[1:]):
            segs_all.append((ln, p, q))
            if abs(p[0] - q[0]) > 0.5 and abs(p[1] - q[1]) > 0.5:
                out.append(("WARN", ln, f"斜线段 {p[0]:g},{p[1]:g}→{q[0]:g},{q[1]:g}（非飞轮类请改直角）"))
            for n in nodes:
                x, y, w, h = n
                if n not in owners and seg_hits_box(p, q, x + 2, y + 2, x + w - 2, y + h - 2):
                    out.append(("ERROR", ln, f"线段穿过节点 {x:g},{y:g},{w:g}×{h:g}"))
                if p[1] == q[1] and any(abs(p[1] - e) <= RIDE for e in (y, y + h)):
                    run = min(max(p[0], q[0]), x + w) - max(min(p[0], q[0]), x)
                    if run > RIDE: out.append(("ERROR", ln, f"水平线段贴着节点 {x:g},{y:g} 的边框跑"))
                if p[0] == q[0] and any(abs(p[0] - e) <= RIDE for e in (x, x + w)):
                    run = min(max(p[1], q[1]), y + h) - max(min(p[1], q[1]), y)
                    if run > RIDE: out.append(("ERROR", ln, f"竖直线段贴着节点 {x:g},{y:g} 的边框跑"))
    for i, (la, a0, a1) in enumerate(segs_all):
        for lb, b0, b1 in segs_all[i + 1:]:
            if la == lb: continue
            for k in (0, 1):  # k=0 水平共线，k=1 竖直共线
                o = 1 - k
                if a0[o] == a1[o] == b0[o] == b1[o]:
                    run = min(max(a0[k], a1[k]), max(b0[k], b1[k])) - max(min(a0[k], a1[k]), min(b0[k], b1[k]))
                    if run > OVERLAP:
                        out.append(("WARN", la, f"和{lb}重叠 {run:g}px"))
    for tpos, ln, s, tx, ty, tw, size in texts:
        box = (tx, ty, tx + tw, ty + size)
        hit = [c for c in conns if c[0] < tpos and any(seg_hits_box(p, q, *box) for p, q in zip(c[2], c[2][1:]))]
        for cpos, cln, _ in hit:
            masked = any(cpos < rp < tpos and f and rx <= box[0] + 2 and ry <= box[1] + 2
                         and rx + rw >= box[2] - 2 and ry + rh >= box[3] - 2
                         for rp, rx, ry, rw, rh, f in rects)
            if not masked:
                out.append(("WARN", ln, f"「{s[:12]}」压在{cln}上，没有垫底色"))
    return out

if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        res = check(f)
        errs = sum(1 for r in res if r[0] == "ERROR")
        bad += errs
        print(f"{'FAIL' if errs else 'ok  '} {f}  ERROR {errs} · WARN {len(res) - errs}")
        for lvl, ln, msg in res:
            print(f"     {lvl:5} {ln}: {msg}")
    sys.exit(1 if bad else 0)
