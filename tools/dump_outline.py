import re, os, sys
COURSE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "course")
pat = sys.argv[1] if len(sys.argv) > 1 else ""
FENCE = chr(96) * 3
for f in sorted(os.listdir(COURSE)):
    if not f.endswith(".md"):
        continue
    if pat and not re.match(pat, f):
        continue
    md = open(os.path.join(COURSE, f), encoding="utf-8").read()
    print("=====", f)
    fence = False
    for ln in md.split("\n"):
        s = ln.strip()
        if s.startswith(FENCE):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^(#{2,3}) (.+)$", ln)
        if m:
            print("  " * (len(m.group(1)) - 2) + m.group(2)[:50])