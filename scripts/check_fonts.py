#!/usr/bin/env python3
"""推送前的硬闸：飞书画板 SVG 里字号过小会在线上折行，而本地 PNG 和 --check 都看不出来。
用法：python3 check_fonts.py board.svg [board2.svg ...]   退出码非 0 表示有问题。
"""
import re, sys

MIN = 13
bad = 0
for path in sys.argv[1:]:
    svg = open(path, encoding="utf-8").read()
    hits = [(m.group(1), svg[max(0, m.end()):m.end() + 90])
            for m in re.finditer(r'font-size="([0-9.]+)"', svg) if float(m.group(1)) < MIN]
    if hits:
        bad += 1
        print(f"✗ {path}：{len(hits)} 处字号 < {MIN}px（线上会折行）")
        for size, ctx in hits[:6]:
            txt = re.sub(r"<[^>]*>", "", ctx)[:40]
            print(f"    {size}px  …{txt}")
    else:
        print(f"✓ {path}")
if bad:
    print(f"\n{bad} 个文件不合格。字号提到 {MIN} 后若出现溢出，请缩短文案或加宽容器，不要再调小字号。")
sys.exit(1 if bad else 0)
