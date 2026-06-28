#!/usr/bin/env python3
# Recolor linen-palette status/structure whiteboards into Geist (eyemvp) green/white style.
# - delete hard offset shadow rects (border-over-shadow)
# - dark headers/strips/badges -> brand green #10A37F
# - linen canvas -> #FAFBFB ; linen cards -> #FFFFFF ; card borders -> #E1E3E4
# - status tints -> Geist semantic tints + matching accent border
# - text -> gray-900 ; header text -> white ; connectors -> gray-700
#
# Usage: python3 recolor_geist.py board-linen.svg [more-linen.svg ...]
# Writes alongside input as board-geist.svg.
import re, sys

# original status fill -> (new tint, accent border)
STATUS = {
    "#D4EDBC": ("#E7F6F0", "#10A37F"),  # green / 已有方案
    "#CFE2F5": ("#E9F1FC", "#3B7DE0"),  # blue  / 已共识
    "#E4D7F2": ("#F0ECF9", "#7E57C2"),  # purple/ 待共创
    "#F8CBC4": ("#FCF2E1", "#E8A23D"),  # amber / 待拍板
}

def attr(line, name):
    m = re.search(name + r'="([^"]*)"', line)
    return m.group(1) if m else None

def num(line, name):
    v = attr(line, name)
    try: return float(v)
    except: return None

def process(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    # collect stroked rects geometry for shadow detection
    stroked = set()
    for ln in lines:
        if "<rect" in ln and "stroke=" in ln:
            x,y,w,h = num(ln,"x"),num(ln,"y"),num(ln,"width"),num(ln,"height")
            if None not in (x,y,w,h):
                stroked.add((round(x),round(y),round(w),round(h)))
    out = []
    for ln in lines:
        s = ln
        if "<rect" in s:
            fill = attr(s, "fill")
            has_stroke = "stroke=" in s
            x,y,w,h = num(s,"x"),num(s,"y"),num(s,"width"),num(s,"height")
            # shadow: dark, no stroke, matches a stroked rect offset by +6,+6
            if (not has_stroke) and fill in ("#1F1A14","#0A0A0A") and None not in (x,y,w,h):
                if (round(x-6),round(y-6),round(w),round(h)) in stroked:
                    continue  # drop shadow
            # recolor fills
            if fill in ("#1F1A14","#0A0A0A"):
                s = s.replace('fill="%s"' % fill, 'fill="#10A37F"')  # header/strip/badge -> green
            elif fill == "#E4D2C4":
                s = s.replace('fill="#E4D2C4"', 'fill="#FFFFFF"' if has_stroke else 'fill="#FAFBFB"')
            elif fill in STATUS:
                tint, acc = STATUS[fill]
                s = s.replace('fill="%s"' % fill, 'fill="%s"' % tint)
                if has_stroke:
                    s = re.sub(r'stroke="[^"]*"', 'stroke="%s"' % acc, s, count=1)
            # generic border recolor (cards / containers) if still dark
            s = re.sub(r'stroke="#1F1A14"', 'stroke="#E1E3E4"', s)
            s = re.sub(r'stroke="#0A0A0A"', 'stroke="#E1E3E4"', s)
            s = re.sub(r'stroke-width="3"', 'stroke-width="2"', s)
        elif "<text" in s:
            s = s.replace('fill="#1F1A14"', 'fill="#1A1E1F"')
            s = s.replace('fill="#E4D2C4"', 'fill="#FFFFFF"')
            s = s.replace('fill="#333333"', 'fill="#6B7173"')
            s = s.replace('fill="#BBBBBB"', 'fill="#6B7173"')
            s = s.replace('fill="#F8CBC4"', 'fill="#FFFFFF"')
        elif "<line" in s or "<polyline" in s:
            s = s.replace('stroke="#1F1A14"', 'stroke="#4A5052"')
        elif "<marker" in s or "<path" in s:
            s = s.replace('fill="#1F1A14"', 'fill="#4A5052"')
        out.append(s)
    open(path.replace("-linen.svg","-geist.svg"), "w", encoding="utf-8").write("\n".join(out))
    print("wrote", path.replace("-linen.svg","-geist.svg"))

for p in sys.argv[1:]:
    process(p)
