#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Geist 绿白 · 定量图表 SVG 生成器（飞书画板可编辑节点）.

5 类经典业务图表，全部只用画板支持的原生元素：rect / circle / line / polyline /
polygon / text，以及少量 <path>（仪表盘弧、桑基流带、面积填充——实测以原生 path 存活）。
不用 gradient / filter / opacity（画板会拍平或忽略）；不设 font-family。

用法：
    from quant_charts import bar_line, gauge, radar, sankey, stacked_area
    svg = bar_line(...)                       # 返回完整 <svg> 字符串
    open('chart.svg','w').write(svg)
然后按 feishu-whiteboard-geist 流程：whiteboard-cli 渲染看图 → --to openapi | lark-cli whiteboard +update 推送。

配色只用 Geist token（见 GEIST 常量）；改数据只改函数入参，别动配色。
"""
import math

# ---- Geist 绿白 token（唯一配色来源）----
GEIST = dict(
    page="#fafbfb", card="#ffffff", border="#e1e3e4", grid="#eef0f0",
    ink="#0a0c0c", body="#1a1e1f", muted="#6b7173", axis="#4a5052",
    green="#10a37f", green_dk="#0b7355", green_lt="#e7f6f0",
    blue="#3b7de0", blue_dk="#2c5fb0", blue_lt="#e9f1fc",
    amber="#e8a23d", amber_dk="#8a5b12", amber_lt="#fcf2e1",
    purple="#7e57c2", purple_lt="#f0ecf9", red="#d9534f",
)
CAT = [GEIST["green"], GEIST["blue"], GEIST["amber"], GEIST["purple"]]  # 分类色序


def _svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><rect x="0" y="0" width="{w}" height="{h}" '
            f'fill="{GEIST["page"]}"/>{body}</svg>')

def _t(x, y, s, size=14, fill=None, weight="normal", anchor="start"):
    fill = fill or GEIST["body"]
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{s}</text>')

def _title(x, y, title, sub=None):
    o = f'<rect x="{x}" y="{y}" width="6" height="22" rx="2" fill="{GEIST["green"]}"/>'
    o += _t(x+16, y+18, title, size=19, fill=GEIST["ink"], weight="bold")
    if sub:
        o += _t(x+16, y+40, sub, size=13, fill=GEIST["muted"])
    return o


def bar_line(title, cats, series_bars, line_series, bar_names, line_name,
             sub=None, y_left="", y_right="", line_unit="%"):
    """分组柱状图 + 趋势折线（双 Y 轴）.
    cats: x 轴分类 ['Q1',...]; series_bars: [[..],[..]] 每组柱的值(1-2组);
    line_series: 折线值(走右轴); bar_names/line_name: 图例名."""
    W, H = 1180, 620
    L, R, T, B = 90, 90, 110, 90
    pw, ph = W-L-R, H-T-B
    o = _title(40, 34, title, sub)
    bmax = max(max(s) for s in series_bars) * 1.15
    lmax = max(line_series) * 1.25
    n = len(cats); slot = pw/n
    # gridlines + left ticks
    for i in range(5):
        gy = T+ph - ph*i/4
        o += f'<line x1="{L}" y1="{gy:.1f}" x2="{L+pw}" y2="{gy:.1f}" stroke="{GEIST["grid"]}" stroke-width="1"/>'
        o += _t(L-10, gy+4, f"{bmax*i/4:.0f}", size=13, fill=GEIST["muted"], anchor="end")
        o += _t(L+pw+10, gy+4, f"{lmax*i/4:.0f}{line_unit}", size=13, fill=GEIST["muted"])
    o += _t(L-10, T-16, y_left, size=13, fill=GEIST["muted"], anchor="end")
    o += _t(L+pw+10, T-16, y_right, size=13, fill=GEIST["muted"])
    # bars
    ng = len(series_bars); bw = min(34, slot*0.6/ng)
    for gi, s in enumerate(series_bars):
        col = CAT[gi]
        for i, v in enumerate(s):
            bh = ph*v/bmax
            bx = L + slot*i + slot/2 - (ng*bw)/2 + gi*bw
            by = T+ph-bh
            o += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="2" fill="{col}"/>'
            o += _t(bx+bw/2, by-6, f"{v:g}", size=13, fill=GEIST["body"], weight="bold", anchor="middle")
    # x labels
    for i, c in enumerate(cats):
        o += _t(L+slot*i+slot/2, T+ph+24, c, size=13, fill=GEIST["body"], anchor="middle")
    # trend line (right axis) - polyline + hollow points
    pts = []
    for i, v in enumerate(line_series):
        px = L+slot*i+slot/2; py = T+ph - ph*v/lmax
        pts.append((px, py))
    o += '<polyline points="'+" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)+f'" fill="none" stroke="{GEIST["amber"]}" stroke-width="3"/>'
    for i, (x, y) in enumerate(pts):
        o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{GEIST["card"]}" stroke="{GEIST["amber"]}" stroke-width="3"/>'
        # % 标签放数据点右上，避开柱顶数值；末点改左上防溢出
        rt = i < len(pts)-1
        o += _t(x+(10 if rt else -10), y-9, f"{line_series[i]:g}{line_unit}", size=13,
                fill=GEIST["amber_dk"], weight="bold", anchor=("start" if rt else "end"))
    # legend
    lx = L
    for gi, nm in enumerate(bar_names):
        o += f'<rect x="{lx}" y="{H-40}" width="14" height="14" rx="2" fill="{CAT[gi]}"/>'+_t(lx+20, H-28, nm, size=13, fill=GEIST["body"]); lx += 30+len(nm)*13
    o += f'<line x1="{lx}" y1="{H-33}" x2="{lx+22}" y2="{H-33}" stroke="{GEIST["amber"]}" stroke-width="3"/>'
    o += f'<circle cx="{lx+11}" cy="{H-33}" r="4" fill="{GEIST["card"]}" stroke="{GEIST["amber"]}" stroke-width="3"/>'+_t(lx+30, H-28, line_name, size=13, fill=GEIST["body"])
    return _svg(W, H, o)


def gauge(title, pct, label, sub=None, center_unit="%"):
    """环形仪表盘 Gauge（270° 弧，单一 KPI）. pct: 0-100."""
    W, H = 620, 560
    cx, cy, rad = W/2, 330, 200
    start, sweep = 135, 270  # 从左下 135° 起，顺时针 270°
    o = _title(40, 34, title, sub)
    def pol(a, r):
        rad_ = math.radians(a)
        return cx + r*math.cos(rad_), cy + r*math.sin(rad_)
    def arc(a0, a1, r, col, width):
        x0, y0 = pol(a0, r); x1, y1 = pol(a1, r)
        large = 1 if (a1-a0) % 360 > 180 else 0
        return (f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large},1 {x1:.1f},{y1:.1f}" '
                f'fill="none" stroke="{col}" stroke-width="{width}" stroke-linecap="round"/>')
    o += arc(start, start+sweep, rad, GEIST["grid"], 26)          # 轨道
    o += arc(start, start+sweep*pct/100, rad, GEIST["green"], 26)  # 进度
    # 11 段刻度
    for i in range(11):
        a = start + sweep*i/10
        x0, y0 = pol(a, rad+18); x1, y1 = pol(a, rad+28)
        o += f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{GEIST["muted"]}" stroke-width="2"/>'
    num = f"{pct:g}"
    o += _t(cx, cy+18, num, size=96, fill=GEIST["ink"], weight="bold", anchor="middle")
    o += _t(cx + len(num)*28 + 6, cy-26, center_unit, size=28, fill=GEIST["muted"], anchor="start")
    # 领先药丸
    o += f'<rect x="{cx-70}" y="{cy+44}" width="140" height="34" rx="17" fill="{GEIST["green_lt"]}"/>'
    o += _t(cx, cy+66, label, size=15, fill=GEIST["green_dk"], weight="bold", anchor="middle")
    return _svg(W, H, o)


def radar(title, axes, series, names, sub=None, rings=4):
    """雷达图（多维对比）. axes: 维度名; series: [[..],[..]] 各 0-100; names: 系列名."""
    W, H = 1080, 640
    cx, cy, rad = 360, 350, 220
    o = _title(40, 34, title, sub)
    N = len(axes)
    def pt(i, v):
        a = math.radians(-90 + 360*i/N)
        r = rad*v/100
        return cx + r*math.cos(a), cy + r*math.sin(a)
    # rings + axes
    for k in range(1, rings+1):
        poly = " ".join(f"{cx+rad*k/rings*math.cos(math.radians(-90+360*i/N)):.1f},{cy+rad*k/rings*math.sin(math.radians(-90+360*i/N)):.1f}" for i in range(N))
        o += f'<polygon points="{poly}" fill="none" stroke="{GEIST["grid"]}" stroke-width="1"/>'
    for i, ax in enumerate(axes):
        ex, ey = pt(i, 100)
        o += f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{GEIST["border"]}" stroke-width="1"/>'
        lx, ly = pt(i, 118)
        o += _t(lx, ly+4, ax, size=13, fill=GEIST["body"], weight="bold", anchor="middle")
    # series polygons (solid light fill, no opacity)
    fills = [GEIST["green_lt"], GEIST["blue_lt"]]
    strokes = [GEIST["green"], GEIST["blue"]]
    for si, s in enumerate(series):
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, v) for i, v in enumerate(s)))
        o += f'<polygon points="{poly}" fill="{fills[si%2]}" fill-opacity="1" stroke="{strokes[si%2]}" stroke-width="2.5"/>'
        for i, v in enumerate(s):
            x, y = pt(i, v)
            o += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{strokes[si%2]}"/>'
    # scorecard
    sx, sy = 660, 150
    o += f'<rect x="{sx}" y="{sy}" width="380" height="{60+len(axes)*34}" rx="8" fill="{GEIST["card"]}" stroke="{GEIST["border"]}" stroke-width="2"/>'
    o += _t(sx+20, sy+30, "维度对比", size=15, fill=GEIST["ink"], weight="bold")
    for i, ax in enumerate(axes):
        yy = sy+58+i*34
        a, b = series[0][i], series[1][i] if len(series) > 1 else 0
        win = strokes[0] if a >= b else strokes[1]
        o += _t(sx+20, yy, ax, size=13, fill=GEIST["body"])
        o += _t(sx+200, yy, f"{a:g}", size=13, fill=strokes[0], weight="bold", anchor="middle")
        o += _t(sx+280, yy, f"{b:g}", size=13, fill=strokes[1], weight="bold", anchor="middle")
        o += f'<circle cx="{sx+350}" cy="{yy-4}" r="5" fill="{win}"/>'
    # legend
    for si, nm in enumerate(names):
        o += f'<rect x="{60+si*160}" y="{H-40}" width="14" height="14" rx="2" fill="{strokes[si%2]}"/>'+_t(80+si*160, H-28, nm, size=13, fill=GEIST["body"])
    return _svg(W, H, o)


def sankey(title, left, mid, flows, sub=None):
    """两层桑基（左→中）流量守恒. left/mid: [(名, 值)]; flows: [(li, mi, 值)]."""
    W, H = 1180, 620
    o = _title(40, 34, title, sub)
    T, Bt = 100, 60; colw = 26
    lx, mx = 120, W-320
    tot = sum(v for _, v in left)
    ph = H-T-Bt
    def layout(nodes, x, col):
        y = T; pos = {}
        for i, (nm, v) in enumerate(nodes):
            h = ph*v/tot
            pos[i] = (x, y, h)
            o_ = f'<rect x="{x}" y="{y:.1f}" width="{colw}" height="{h:.1f}" rx="3" fill="{col(i)}"/>'
            o_ += _t(x+ (colw+8 if x < W/2 else -8), y+h/2+4, f"{nm} {v:g}", size=13, fill=GEIST["body"], anchor=("start" if x < W/2 else "end"))
            pos[i] = (x, y, h, o_)
            y += h + 10
        return pos
    lpos = layout(left, lx, lambda i: CAT[i % len(CAT)])
    mpos = layout(mid, mx, lambda i: GEIST["muted"])
    # flow bands (cubic bezier path, colored by source)
    lcur = {i: lpos[i][1] for i in lpos}
    mcur = {i: mpos[i][1] for i in mpos}
    bands = ""
    for li, mi, v in flows:
        h = ph*v/tot
        x0 = lx+colw; x1 = mx
        y0 = lcur[li]; y1 = mcur[mi]
        xc = (x0+x1)/2
        col = CAT[li % len(CAT)]
        bands += (f'<path d="M{x0},{y0:.1f} C{xc},{y0:.1f} {xc},{y1:.1f} {x1},{y1:.1f} '
                  f'L{x1},{y1+h:.1f} C{xc},{y1+h:.1f} {xc},{y0+h:.1f} {x0},{y0+h:.1f} Z" '
                  f'fill="{col}"/>')
        lcur[li] += h; mcur[mi] += h
    o += bands  # bands behind nodes
    for p in list(lpos.values())+list(mpos.values()):
        o += p[3]
    return _svg(W, H, o)


def stacked_area(title, xs, layers, names, sub=None, y_unit=""):
    """堆叠面积图. xs: x 标签; layers: [[..],[..],..] 各层值; names: 层名."""
    W, H = 1180, 600
    L, R, T, B = 80, 60, 100, 80
    pw, ph = W-L-R, H-T-B
    o = _title(40, 34, title, sub)
    n = len(xs)
    cum = [0]*n
    tops = []
    for layer in layers:
        cum = [c+v for c, v in zip(cum, layer)]
        tops.append(cum[:])
    ymax = max(cum)*1.12
    for i in range(5):
        gy = T+ph-ph*i/4
        o += f'<line x1="{L}" y1="{gy:.1f}" x2="{L+pw}" y2="{gy:.1f}" stroke="{GEIST["grid"]}" stroke-width="1"/>'
        o += _t(L-10, gy+4, f"{ymax*i/4:.0f}", size=13, fill=GEIST["muted"], anchor="end")
    o += _t(L-10, T-16, y_unit, size=13, fill=GEIST["muted"], anchor="end")
    def X(i): return L + pw*i/(n-1)
    def Y(v): return T+ph - ph*v/ymax
    prev = [0]*n
    for li, top in enumerate(tops):
        col = CAT[li % len(CAT)]
        # area path: top edge L->R, bottom edge R->L
        d = "M"+" L".join(f"{X(i):.1f},{Y(top[i]):.1f}" for i in range(n))
        d += " L"+" L".join(f"{X(i):.1f},{Y(prev[i]):.1f}" for i in range(n-1, -1, -1))+" Z"
        o += f'<path d="{d}" fill="{col}"/>'
        prev = top[:]
    # global top outline points
    for i in range(n):
        o += f'<circle cx="{X(i):.1f}" cy="{Y(tops[-1][i]):.1f}" r="4" fill="{GEIST["card"]}" stroke="{GEIST["green_dk"]}" stroke-width="2"/>'
    for i, x in enumerate(xs):
        o += _t(X(i), T+ph+24, x, size=13, fill=GEIST["body"], anchor="middle")
    for li, nm in enumerate(names):
        o += f'<rect x="{L+li*150}" y="{H-38}" width="14" height="14" rx="2" fill="{CAT[li%len(CAT)]}"/>'+_t(L+20+li*150, H-26, nm, size=13, fill=GEIST["body"])
    return _svg(W, H, o)


if __name__ == "__main__":
    import os
    d = os.path.dirname(os.path.abspath(__file__))
    demos = {
        "bar_line": bar_line("季度营收 vs 利润率", ["Q1", "Q2", "Q3", "Q4"],
            [[120, 150, 180, 210], [100, 118, 132, 150]], [8, 11, 14, 18],
            ["今年营收", "去年同期"], "利润率", sub="规模与质量同框", y_left="营收(万元)", y_right="利润率"),
        "gauge": gauge("季度目标完成度", 78, "领先进度 · Top 10%", sub="单一 KPI 一眼读懂"),
        "radar": radar("产品选型 · 六维对比", ["性能", "价格", "生态", "易用", "安全", "扩展"],
            [[85, 60, 90, 75, 80, 70], [70, 88, 65, 85, 72, 80]], ["方案 A", "方案 B"], sub="谁强在哪一目了然"),
        "sankey": sankey("流量转化 · 来源→落地", [("自然搜索", 30), ("社媒", 22), ("直投", 18), ("邮件", 15)],
            [("首页", 40), ("详情页", 28), ("活动页", 17)],
            [(0, 0, 18), (0, 1, 12), (1, 0, 12), (1, 2, 10), (2, 1, 10), (2, 2, 8), (3, 0, 10), (3, 1, 5)], sub="流量守恒"),
        "stacked_area": stacked_area("三产品月活堆叠", ["1月", "2月", "3月", "4月", "5月", "6月"],
            [[30, 34, 38, 42, 48, 55], [25, 28, 30, 35, 40, 44], [15, 20, 26, 33, 40, 48]],
            ["产品 A", "产品 B", "产品 C"], sub="增量来源看得清", y_unit="MAU(万)"),
    }
    for name, svg in demos.items():
        open(os.path.join(d, f"_demo_{name}.svg"), "w", encoding="utf-8").write(svg)
        print("wrote", name)
