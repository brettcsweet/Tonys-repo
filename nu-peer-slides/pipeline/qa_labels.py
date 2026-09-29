"""Label-fit QA on a rendered deck PDF: word-box overlaps and out-of-bounds text."""
import sys, pymupdf
pdf = sys.argv[1]
d = pymupdf.open(pdf)
tot = 0
for pi, pg in enumerate(d, 1):
    W, H = pg.rect.width, pg.rect.height
    words = pg.get_text("words")   # x0,y0,x1,y1,text,block,line,wordno
    issues = []
    for w in words:
        if w[0] < 0 or w[1] < 0 or w[2] > W or w[3] > H:
            issues.append(("OUT-OF-SLIDE", w[4], [round(v) for v in w[:4]]))
        # 0.3in safe margin on right/bottom for non-footer text
        if w[2] > W - 0.3 * 72 and w[1] < H - 0.7 * 72:
            issues.append(("NEAR-RIGHT-EDGE", w[4], [round(v) for v in w[:4]]))
    for i in range(len(words)):
        a = words[i]
        for j in range(i + 1, len(words)):
            b = words[j]
            ox = min(a[2], b[2]) - max(a[0], b[0]); oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 1.0 and oy > 2.5:
                issues.append(("OVERLAP", a[4] + " | " + b[4], [round(a[0]), round(a[1]), round(b[0]), round(b[1])]))
    print(f"slide {pi}: {len(words)} words, {len(issues)} issues")
    for it in issues[:40]: print("   ", it)
    tot += len(issues)
print("TOTAL issues:", tot)
