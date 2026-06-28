#!/usr/bin/env python3
# Categorical Geist recolor for skeleton / roadmap (branch & session color-coding).
# Usage: python3 recolor_geist_cat.py board-linen.svg [...]  -> writes board-geist.svg
import re, sys
def attr(line,n):
    m=re.search(n+r'="([^"]*)"',line); return m.group(1) if m else None
def process(path):
    out=[]
    for s in open(path,encoding="utf-8").read().split("\n"):
        if "<rect" in s:
            fill=attr(s,"fill"); has_stroke="stroke=" in s
            if fill=="#1F1A14":   s=s.replace('fill="#1F1A14"','fill="#0A0C0C"')   # neutral dark
            elif fill=="#044D99": s=s.replace('fill="#044D99"','fill="#3B7DE0"')   # info blue
            elif fill=="#04B24F": s=s.replace('fill="#04B24F"','fill="#10A37F"')   # brand green
            elif fill=="#F61B27": s=s.replace('fill="#F61B27"','fill="#E8A23D"')   # amber
            elif fill=="#E4D2C4": s=s.replace('fill="#E4D2C4"','fill="#FFFFFF"' if has_stroke else 'fill="#FAFBFB"')
            s=re.sub(r'stroke="#1F1A14"','stroke="#E1E3E4"',s)
            s=re.sub(r'stroke-width="3"','stroke-width="2"',s)
        elif "<text" in s:
            s=s.replace('fill="#1F1A14"','fill="#1A1E1F"').replace('fill="#E4D2C4"','fill="#FFFFFF"').replace('fill="#333333"','fill="#6B7173"')
        elif "<line" in s or "<polyline" in s:
            s=s.replace('stroke="#1F1A14"','stroke="#4A5052"')
        elif "<marker" in s or "<path" in s:
            s=s.replace('fill="#1F1A14"','fill="#4A5052"')
        out.append(s)
    open(path.replace("-linen.svg","-geist.svg"),"w",encoding="utf-8").write("\n".join(out))
    print("wrote",path.replace("-linen.svg","-geist.svg"))
for p in sys.argv[1:]: process(p)
