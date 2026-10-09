# -*- coding: utf-8 -*-
"""8 种扩展范式的示例板（数据全部虚构）：瀑布 / 时序 / 飞轮 / 架构前后对比 / ER / 热力 / 斜率 / 哑铃。

用法：python3 pattern_examples.py [输出目录]   默认输出到 ../assets/patterns/
做同类图时复制对应函数改数据，别从零算坐标；画法与上限见 references/patterns.md 十一～十八。
辅助函数 arrow / poly / dline / masklabel / box 可直接 import 复用。
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geist_layout as gl
from geist_layout import G, T, RECT, LINE, head, strip, card, _units

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "patterns")) + "/"
LINK = "#4A5052"
DEFS = ('<defs><marker id="a" markerWidth="12" markerHeight="12" refX="9" refY="4" orient="auto" '
        'markerUnits="strokeWidth"><path d="M0 0 L10 4 L0 8 z"/></marker></defs>')

def save(p, name, h):
    W = gl.W
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">'
           + DEFS + RECT(0, 0, W, h, G["page"]) + "".join(p) + "</svg>")
    open(OUT + name, "w", encoding="utf-8").write(svg)
    print("wrote", name)

def arrow(x1, y1, x2, y2, c=LINK, w=2, dash=False):
    d = ' stroke-dasharray="6 5"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" '
            f'stroke-width="{w}"{d} marker-end="url(#a)"/>')

def poly(pts, c=LINK, w=2, mark=True, dash=False):
    s = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = ' stroke-dasharray="6 5"' if dash else ""
    m = ' marker-end="url(#a)"' if mark else ""
    return f'<polyline points="{s}" fill="none" stroke="{c}" stroke-width="{w}"{d}{m}/>'

def dline(x1, y1, x2, y2, c=G["bd"], w=1):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" '
            f'stroke-width="{w}" stroke-dasharray="4 4"/>')

def masklabel(p, cx, cy, s, size=14, fill=None, w="normal", bg=None):
    """标签垫不透明底色，压在线上也读得清（diagram-design 的 label mask 规则）。"""
    tw = _units(s) * size + 16
    p.append(RECT(cx - tw / 2, cy - size - 4, tw, size + 12, bg or G["page"], rx=4))
    p.append(T(cx, cy + 2, s, size, fill or G["body"], w, "middle"))

def box(p, x, y, w, h, title, sub=None, status="gray", dash=False, solid=None):
    bg, bd, fg = gl.ST[status]
    fillc = solid or (G["card"] if status == "gray" else bg)
    s = RECT(x, y, w, h, fillc, bd, rx=8)
    if dash: s = s.replace("/>", ' stroke-dasharray="7 5"/>')
    p.append(s)
    tc = "#FFFFFF" if solid else (G["ink"] if status == "gray" else fg)
    if sub:
        p.append(T(x + w / 2, y + h / 2 - 3, title, 17, tc, "700", "middle"))
        p.append(T(x + w / 2, y + h / 2 + 20, sub, 14, "#FFFFFF" if solid else G["muted"], anchor="middle"))
    else:
        p.append(T(x + w / 2, y + h / 2 + 6, title, 17, tc, "700", "middle"))

# ---------------------------------------------------------------- 1 瀑布图
def waterfall():
    p = []
    head(p, "9 月 渠道佣金环比拆解", "单位：百万 NGN")
    steps = [("8 月佣金", 42.0, "t"), ("新商户", 6.8, "+"), ("存量增长", 3.1, "+"),
             ("流失商户", -4.6, "-"), ("佣金封顶", -2.2, "-"), ("费率调整", -1.5, "-"), ("9 月佣金", 43.6, "t")]
    x0, x1, yb, ytop, vmax = 170, 1600, 720, 170, 55.0
    sc = (yb - ytop) / vmax
    for v in range(0, 60, 10):
        y = yb - v * sc
        p.append(LINE(x0, y, x1, y, G["grid"] if v else G["bd"], 1 if v else 2))
        p.append(T(x0 - 16, y + 5, str(v), 14, G["muted"], anchor="end"))
    slot = (x1 - x0) / len(steps); bw = 116
    run = 0.0; prev_top = None
    for i, (name, v, k) in enumerate(steps):
        cx = x0 + slot * (i + 0.5); bx = cx - bw / 2
        if k == "t":
            lo, hi = 0, v; run = v; fc, sc_ = G["ink"], None; lab = f"{v:.1f}"; lc = G["ink"]
        else:
            lo, hi = (run, run + v) if v > 0 else (run + v, run); run += v
            fc, sc_ = (G["green_lt"], G["green"]) if v > 0 else (G["amber_lt"], G["amber"])
            lab = f"+{v:.1f}" if v > 0 else f"−{abs(v):.1f}"
            lc = G["green_dk"] if v > 0 else G["amber_dk"]
        yt, yl = yb - hi * sc, yb - lo * sc
        p.append(RECT(bx, yt, bw, yl - yt, fc, sc_, rx=3))
        p.append(T(cx, yt - 14, lab, 18, lc, "700", "middle"))
        p.append(T(cx, yb + 32, name, 15, G["body"], anchor="middle"))
        if prev_top is not None:  # 前一根柱末端 → 本柱起点的虚线
            p.append(dline(prev_top[0], prev_top[1], bx, prev_top[1], LINK))
        yend = yb - run * sc
        prev_top = (bx + bw, yend)
    strip(p, 790, "环比 +1.6M（+3.8%）：新商户贡献 6.8M，抵掉了流失 4.6M 与封顶 2.2M；封顶已是第二大拖累项")
    save(p, "01_waterfall.svg", 880)

# ---------------------------------------------------------------- 2 时序图
def sequence():
    p = []
    head(p, "商户转移审批 · 时序", "1 期流程")
    actors = ["代理商 App", "运营后台", "风控", "原代理商", "商户"]
    xs = [200 + i * 320 for i in range(5)]
    for i, (a, x) in enumerate(zip(actors, xs)):
        solid = G["ink"] if i == 1 else None
        box(p, x - 110, 120, 220, 56, a, status="gray", solid=solid)
        p.append(dline(x, 176, x, 860, "#B9BEC0", 2))
    # 运营后台激活条
    p.append(RECT(xs[1] - 9, 220, 18, 590, G["card"], G["bd"], rx=2))
    msgs = [(0, 1, "提交转移申请", "main"), (1, 2, "校验关联账号风险", "n"),
            (2, 1, "返回风险等级", "ret"), (1, 3, "推送待确认通知", "n"),
            (3, 1, "同意，或 72h 超时默认同意", "ret"), (1, 4, "变更归属并短信告知", "main"),
            (1, 0, "转移完成", "ret")]
    y = 260
    for a, b, lab, kind in msgs:
        xa, xb = xs[a], xs[b]
        # 起止点落在激活条边缘，不扎进生命线
        sx = xa + (9 if a == 1 and xb > xa else -9 if a == 1 else 0)
        ex = xb + (9 if b == 1 and xa > xb else -9 if b == 1 else 0)
        c = G["green"] if kind == "main" else LINK
        p.append(arrow(sx, y, ex - (6 if ex > sx else -6), y, c, 3 if kind == "main" else 2, kind == "ret"))
        masklabel(p, (sx + ex) / 2, y - 14, lab, 15, G["green_dk"] if kind == "main" else G["body"],
                  "700" if kind == "main" else "normal")
        y += 80
    # 图例（底部横条）
    ly = 880
    p.append(LINE(60, ly, 120, ly, G["green"], 3)); p.append(T(132, ly + 5, "主路径", 14, G["muted"]))
    p.append(LINE(230, ly, 290, ly, LINK, 2)); p.append(T(302, ly + 5, "同步调用", 14, G["muted"]))
    p.append(dline(420, ly, 480, ly, LINK, 2)); p.append(T(492, ly + 5, "返回 / 回调", 14, G["muted"]))
    strip(p, 910, "关键等待点在原代理商确认：72h 不回视为同意，避免卡单；风控只给等级不直接拦截")
    save(p, "02_sequence.svg", 1000)

# ---------------------------------------------------------------- 3 闭环飞轮
def flywheel():
    p = []
    head(p, "渠道增长飞轮", "9 月环比")
    cx, cy, R = 840, 500, 300
    nodes = [("拉新商户", "+1,240 户"), ("交易增长", "GTV +6.2%"), ("佣金增加", "+3.8%"),
             ("代理商升级", "升级 37 家"), ("资源倾斜", "物料与额度")]
    bw, bh = 230, 84
    pos = []
    for i in range(5):
        ang = math.radians(-90 + 72 * i)
        pos.append((cx + R * math.cos(ang), cy + R * 0.92 * math.sin(ang)))
    for i in range(5):
        (ax, ay), (bx, by) = pos[i], pos[(i + 1) % 5]
        dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
        t = min(bw / 2 / max(abs(ux), 1e-6), bh / 2 / max(abs(uy), 1e-6)) + 12
        p.append(arrow(ax + ux * t, ay + uy * t, bx - ux * (t + 4), by - uy * (t + 4), LINK, 3))
    for i, ((x, y), (t1, t2)) in enumerate(zip(pos, nodes)):
        box(p, x - bw / 2, y - bh / 2, bw, bh, t1, t2, status="green" if i == 0 else "gray")
    p.append(f'<circle cx="{cx}" cy="{cy}" r="96" fill="{G["green"]}"/>')
    p.append(T(cx, cy - 4, "渠道", 26, "#FFFFFF", "700", "middle"))
    p.append(T(cx, cy + 26, "增长飞轮", 17, "#FFFFFF", "700", "middle"))
    # 阻力：挂在「拉新→交易」这条边外侧
    (ax, ay), (bx, by) = pos[0], pos[1]
    mx, my = (ax + bx) / 2 + 150, (ay + by) / 2 - 40
    p.append(RECT(mx, my, 260, 70, G["amber_lt"], G["amber"], rx=8))
    p.append(T(mx + 130, my + 30, "阻力：商户被搬", 16, G["amber_dk"], "700", "middle"))
    p.append(T(mx + 130, my + 54, "9 月转出 412 户", 14, G["amber_dk"], anchor="middle"))
    strip(p, 810, "飞轮起点是拉新，最大阻力在拉新到交易之间的商户被搬；转移审批上线就是在给这段减阻")
    save(p, "03_flywheel.svg", 900)

# ---------------------------------------------------------------- 4 架构前后对比
def arch_delta():
    p = []
    head(p, "商户转移 · 系统架构前后对比", "1 期")
    bw, bh = 280, 72
    for k, (px, title) in enumerate([(40, "现状"), (860, "1 期上线后")]):
        p.append(RECT(px, 112, 780, 470, G["card"], G["bd"], rx=8))
        p.append(T(px + 28, 150, title, 20, G["ink"], "700"))
        L, Rx = px + 50, px + 450
        r1, r2, r3 = 190, 330, 470
        box(p, L, r1, bw, bh, "代理商 App"); box(p, Rx, r1, bw, bh, "运营后台")
        box(p, L, r2, bw, bh, "商户管理服务")
        if k == 0:
            box(p, Rx, r2, bw, bh, "线下表格审批", "人工逐单核对", status="amber", dash=True)
            box(p, L, r3, bw, bh, "商户归属表")
            lab = "人工录入"
        else:
            box(p, Rx, r2, bw, bh, "转移审批服务", "新增", status="green")
            box(p, L, r3, bw, bh, "商户归属表", "改造：加转移记录", status="blue")
            box(p, Rx, r3, bw, bh, "风控校验", "新增：关联账号判定", status="green")
            p.append(arrow(Rx + bw / 2, r2 + bh, Rx + bw / 2, r3 - 6, G["green"], 3))
            lab = "自动回写"
        p.append(arrow(L + bw / 2, r1 + bh, L + bw / 2, r2 - 6))
        p.append(arrow(Rx + bw / 2, r1 + bh, Rx + bw / 2, r2 - 6, G["green"] if k else LINK, 3 if k else 2))
        p.append(arrow(Rx, r2 + bh / 2, L + bw + 6, r2 + bh / 2, G["green"] if k else LINK, 3 if k else 2, k == 0))
        masklabel(p, (Rx + L + bw) / 2, r2 + bh / 2 - 12, lab, 14, G["green_dk"] if k else G["amber_dk"], bg=G["card"])
        p.append(arrow(L + bw / 2, r2 + bh, L + bw / 2, r3 - 6))
    # 中间的「→」
    p.append(arrow(824, 347, 852, 347, G["ink"], 3))
    # 变更清单
    p.append(RECT(40, 606, 1600, 196, G["card"], G["bd"], rx=8))
    p.append(T(68, 644, "变更清单", 18, G["ink"], "700"))
    rows = [("新增", "green", "转移审批服务", "替代线下表格，审批结果自动回写商户管理服务"),
            ("新增", "green", "风控校验", "关联账号判定 + 重复绑定识别，只给等级不拦截"),
            ("改造", "blue", "商户归属表", "加转移记录字段，可追溯每次归属变更"),
            ("下线", "amber", "线下表格审批", "1 期上线后两周内停用")]
    for i, (tag, st, name, desc) in enumerate(rows):
        y = 676 + i * 30
        bg, bd, fg = gl.ST[st]
        p.append(RECT(68, y - 17, 56, 24, bg, bd, rx=4))
        p.append(T(96, y + 1, tag, 13, fg, "700", "middle"))
        p.append(T(144, y + 1, name, 15, G["ink"], "700"))
        p.append(T(340, y + 1, desc, 15, G["body"]))
    strip(p, 822, "核心变化只有一条：转移审批从线下表格搬进系统，并接上风控校验；其余服务不动")
    save(p, "04_arch_delta.svg", 910)

# ---------------------------------------------------------------- 5 ER 图
def er():
    p = []
    head(p, "商户归属 · 数据模型", "5 张核心表")
    ents = {
        "agg": (90, 150, "代理商 agent", [("agent_id", "PK"), ("名称", ""), ("等级", ""), ("客户经理", ""), ("创建时间", "")], "gray"),
        "mch": (690, 150, "商户 merchant", [("merchant_id", "PK"), ("agent_id", "FK"), ("B/C 标签", ""), ("状态", ""), ("注册时间", "")], "green"),
        "txn": (1290, 150, "交易 transaction", [("txn_id", "PK"), ("merchant_id", "FK"), ("金额 NGN", ""), ("交易类型", ""), ("交易时间", "")], "gray"),
        "com": (90, 530, "佣金结算 settlement", [("settle_id", "PK"), ("agent_id", "FK"), ("结算月", ""), ("佣金 NGN", ""), ("封顶标记", "")], "gray"),
        "trf": (690, 530, "转移记录 transfer", [("transfer_id", "PK"), ("merchant_id", "FK"), ("from_agent_id", "FK"), ("to_agent_id", "FK"), ("审批状态", "")], "amber"),
    }
    W_, HH, RH = 300, 48, 34
    for key, (x, y, name, fields, st) in ents.items():
        h = HH + RH * len(fields) + 8
        bg, bd, fg = gl.ST[st]
        p.append(RECT(x, y, W_, h, G["card"], bd if st != "gray" else G["bd"], rx=8))
        hfill = G["green"] if st == "green" else (G["amber_lt"] if st == "amber" else G["page"])
        p.append(RECT(x + 2, y + 2, W_ - 4, HH - 2, hfill, rx=6))
        p.append(T(x + 18, y + 31, name, 17, "#FFFFFF" if st == "green" else (G["amber_dk"] if st == "amber" else G["ink"]), "700"))
        if st == "amber":
            p.append(T(x + W_ - 16, y + 31, "1 期新增", 13, G["amber_dk"], "700", "end"))
        for i, (f, tag) in enumerate(fields):
            fy = y + HH + RH * i + 24
            if i: p.append(LINE(x + 12, fy - 22, x + W_ - 12, fy - 22, G["grid"]))
            p.append(T(x + 18, fy, f, 15, G["body"], "700" if tag == "PK" else "normal"))
            if tag: p.append(T(x + W_ - 18, fy, tag, 13, G["green_dk"] if tag == "PK" else G["muted"], "700", "end"))
    bot = lambda k: ents[k][1] + HH + RH * 5 + 8
    def card_lab(x, y, s, anchor="start"):
        p.append(T(x, y, s, 15, G["green_dk"], "700", anchor))
    # 代理商 1—N 商户
    y1 = 150 + HH + 24 - 6
    p.append(LINE(390, 240, 690, 240, LINK, 2)); card_lab(402, 230, "1"); card_lab(678, 230, "N", "end")
    masklabel(p, 540, 228, "名下商户", 14)
    # 商户 1—N 交易
    p.append(LINE(990, 240, 1290, 240, LINK, 2)); card_lab(1002, 230, "1"); card_lab(1278, 230, "N", "end")
    masklabel(p, 1140, 228, "产生交易", 14)
    # 代理商 1—N 佣金结算
    p.append(LINE(170, bot("agg"), 170, 530, LINK, 2)); card_lab(180, bot("agg") + 22, "1"); card_lab(180, 520, "N")
    masklabel(p, 250, (bot("agg") + 530) / 2 + 6, "按月结算", 14)
    # 商户 1—N 转移记录
    p.append(LINE(840, bot("mch"), 840, 530, LINK, 2)); card_lab(850, bot("mch") + 22, "1"); card_lab(850, 520, "N")
    masklabel(p, 920, (bot("mch") + 530) / 2 + 6, "归属变更", 14)
    # 代理商 1—N 转移记录（转出/转入），正交走线
    p.append(poly([(390, 330), (540, 330), (540, 640), (690, 640)], LINK, 2, mark=False))
    card_lab(402, 320, "1"); card_lab(678, 630, "N", "end")
    masklabel(p, 540, 480, "转出 / 转入", 14)
    # 图例卡
    lx, ly = 1290, 530
    p.append(RECT(lx, ly, 300, 160, G["card"], G["bd"], rx=8))
    p.append(T(lx + 18, ly + 34, "图例", 16, G["ink"], "700"))
    for i, (a, b) in enumerate([("PK", "主键"), ("FK", "外键"), ("1 — N", "一对多")]):
        p.append(T(lx + 18, ly + 70 + i * 30, a, 15, G["green_dk"], "700"))
        p.append(T(lx + 100, ly + 70 + i * 30, b, 15, G["body"]))
    strip(p, 800, "商户是中心表；转移记录同时挂商户和两次代理商（转出/转入），归属历史从此可查")
    save(p, "05_er.svg", 890)

# ---------------------------------------------------------------- 6 热力图
def heatmap():
    p = []
    head(p, "各州商户活跃率 · 月度热力", "活跃率 %")
    rows = ["Lagos", "Abuja", "Oyo", "Rivers", "Kano", "Kaduna"]
    cols = ["4 月", "5 月", "6 月", "7 月", "8 月", "9 月"]
    data = [[68, 70, 71, 73, 74, 76], [61, 62, 64, 63, 66, 67], [55, 57, 56, 58, 60, 61],
            [58, 57, 55, 52, 49, 47], [44, 46, 47, 31, 45, 48], [39, 40, 42, 43, 43, 45]]
    bins = [(40, "#F1F8F5", G["body"]), (50, "#CFEBDF", G["body"]), (60, "#8FD1B6", G["ink"]),
            (70, "#3DB58C", "#FFFFFF"), (101, "#0B7355", "#FFFFFF")]
    def col(v):
        for t, c, tc in bins:
            if v < t: return c, tc
    x0, y0, cw, ch = 260, 190, 200, 76
    for j, c in enumerate(cols):
        p.append(T(x0 + cw * j + cw / 2, y0 - 18, c, 15, G["muted"], "700", "middle"))
    for i, r in enumerate(rows):
        p.append(T(x0 - 24, y0 + ch * i + ch / 2 + 6, r, 16, G["ink"], "700", "end"))
        for j, v in enumerate(data[i]):
            c, tc = col(v)
            p.append(RECT(x0 + cw * j + 2, y0 + ch * i + 2, cw - 4, ch - 4, c, rx=4))
            p.append(T(x0 + cw * j + cw / 2, y0 + ch * i + ch / 2 + 7, f"{v}%", 18, tc, "700", "middle"))
    # 异常格：Kano 7 月
    p.append(RECT(x0 + cw * 3 - 1, y0 + ch * 4 - 1, cw + 2, ch + 2, "none", G["amber"], rx=6, sw=4))
    p.append(T(x0 + cw * 6 + 30, y0 + ch * 4 + 32, "Kano 7 月骤降", 16, G["amber_dk"], "700"))
    p.append(T(x0 + cw * 6 + 30, y0 + ch * 4 + 56, "雨季断网，8 月恢复", 14, G["amber_dk"]))
    p.append(T(x0 + cw * 6 + 30, y0 + ch * 3 + 32, "Rivers 连降 5 月", 16, G["amber_dk"], "700"))
    p.append(T(x0 + cw * 6 + 30, y0 + ch * 3 + 56, "58% 到 47%", 14, G["amber_dk"]))
    # 色阶图例
    ly = y0 + ch * 6 + 40
    p.append(T(x0, ly + 20, "色阶", 14, G["muted"], "700"))
    labs = ["40 以下", "40–50", "50–60", "60–70", "≥ 70"]
    for k, (t, c, tc) in enumerate(bins):
        p.append(RECT(x0 + 60 + k * 120, ly, 110, 30, c, rx=3))
        p.append(T(x0 + 115 + k * 120, ly + 21, labs[k], 13, tc, "700", "middle"))
    strip(p, ly + 70, "Lagos 稳步走高；Rivers 是唯一持续下滑的州，需要单独排查；Kano 7 月是一次性外因")
    save(p, "06_heatmap.svg", ly + 160)

# ---------------------------------------------------------------- 7 斜率图
def slope():
    p = []
    head(p, "各州代理商达标率 · Q2 → Q3", "合格率 %")
    data = [("Lagos", 58, 64), ("Abuja", 52, 56), ("Oyo", 43, 48), ("Rivers", 47, 40),
            ("Kano", 37, 35), ("Kaduna", 31, 31), ("Enugu", 25, 27)]
    xl, xr, ytop, ybot, lo, hi = 560, 1120, 190, 740, 20, 70
    Y = lambda v: ybot - (v - lo) / (hi - lo) * (ybot - ytop)
    p.append(LINE(xl, ytop - 20, xl, ybot + 10, G["bd"], 2)); p.append(LINE(xr, ytop - 20, xr, ybot + 10, G["bd"], 2))
    p.append(T(xl, ytop - 36, "Q2", 18, G["ink"], "700", "middle")); p.append(T(xr, ytop - 36, "Q3", 18, G["ink"], "700", "middle"))
    hl = {"Lagos": (G["green"], G["green_dk"]), "Rivers": (G["amber"], G["amber_dk"])}
    for name, a, b in sorted(data, key=lambda d: d[0] in hl):  # 高亮的后画，压在灰线上面
        c, tc = hl.get(name, ("#C4C8C9", G["muted"]))
        wt = "700" if name in hl else "normal"
        p.append(LINE(xl, Y(a), xr, Y(b), c, 4 if name in hl else 2))
        p.append(f'<circle cx="{xl}" cy="{Y(a):.1f}" r="7" fill="{c}"/>')
        p.append(f'<circle cx="{xr}" cy="{Y(b):.1f}" r="7" fill="{c}"/>')
        p.append(T(xl - 24, Y(a) + 6, f"{name}  {a}%", 16, tc if name in hl else G["body"], wt, "end"))
        d = b - a; ds = f"+{d}" if d > 0 else ("±0" if d == 0 else f"−{abs(d)}")
        p.append(T(xr + 24, Y(b) + 6, f"{b}%  {name}", 16, tc if name in hl else G["body"], wt))
        p.append(T(xr + 210, Y(b) + 6, ds, 16, tc, "700", "end"))
    strip(p, 800, "7 个州里 5 个上升；Lagos 涨幅最大（+6），Rivers 是唯一明显下滑（−7），和热力图的活跃率走势一致")
    save(p, "07_slope.svg", 890)

# ---------------------------------------------------------------- 8 哑铃图
def dumbbell():
    p = []
    head(p, "9 月各州 GTV · 目标 vs 实际", "十亿 NGN")
    data = [("Lagos", 12.0, 13.1), ("Abuja", 8.0, 7.6), ("Oyo", 5.5, 5.9), ("Rivers", 5.0, 3.8),
            ("Kano", 4.2, 4.4), ("Kaduna", 3.0, 2.9), ("Enugu", 2.4, 2.6)]
    x0, x1, vmax, y0, rh = 300, 1340, 14, 200, 76
    X = lambda v: x0 + v / vmax * (x1 - x0)
    for v in range(0, 15, 2):
        p.append(LINE(X(v), y0 - 20, X(v), y0 + rh * len(data) - 30, G["grid"], 1))
        p.append(T(X(v), y0 + rh * len(data) - 4, str(v), 14, G["muted"], anchor="middle"))
    p.append(T(1500, y0 - 34, "达成率", 15, G["muted"], "700", "middle"))
    for i, (n, t, a) in enumerate(data):
        y = y0 + rh * i + 10
        miss = a < t * 0.9
        c, tc = (G["amber"], G["amber_dk"]) if miss else ((G["green"], G["green_dk"]) if a >= t else ("#8E9496", G["body"]))
        p.append(T(x0 - 30, y + 6, n, 17, G["ink"], "700", "end"))
        p.append(LINE(X(min(a, t)), y, X(max(a, t)), y, "#C4C8C9", 6))
        p.append(f'<circle cx="{X(t):.1f}" cy="{y}" r="10" fill="{G["card"]}" stroke="#8E9496" stroke-width="3"/>')
        p.append(f'<circle cx="{X(a):.1f}" cy="{y}" r="11" fill="{c}"/>')
        p.append(T(1500, y + 6, f"{a / t * 100:.0f}%", 18, tc, "700", "middle"))
    # 图例
    ly = 150
    p.append(f'<circle cx="320" cy="{ly}" r="9" fill="{G["card"]}" stroke="#8E9496" stroke-width="3"/>')
    p.append(T(338, ly + 5, "目标", 14, G["muted"]))
    bx = 400
    for k, (c, s) in enumerate([(G["green"], "达成"), ("#8E9496", "差 10% 以内"), (G["amber"], "差 10% 以上")]):
        bx += 20 if k == 0 else _units(prev) * 14 + 60
        prev = s
        p.append(f'<circle cx="{bx}" cy="{ly}" r="9" fill="{c}"/>'); p.append(T(bx + 18, ly + 5, s, 14, G["muted"]))
    strip(p, y0 + rh * len(data) + 30, "7 个州 4 个达成；Rivers 只完成 76%，是唯一差距超 10% 的州，缺口 1.2B")
    save(p, "08_dumbbell.svg", y0 + rh * len(data) + 120)

if __name__ == "__main__":
  for f in (waterfall, sequence, flywheel, arch_delta, er, heatmap, slope, dumbbell):
    f()
