"""Prepare the base .pptx from the official NU white template.

- converts .potx -> .pptx content type
- adds one custom layout ("NU chart slide") with title / subtitle / source-footer placeholders,
  red dash at the left margin (as in the official template), black footer rule and
  "Northeastern University" at bottom right
- patches the off-brand theme palette (cyan / beige accents, near-red D31B2C)
- drops the stale docProps thumbnail and rewrites app.xml
Sample slides are removed later by python-pptx (build_deck.py).
"""
import re, shutil, sys, zipfile, os
from pathlib import Path

SRC = Path(sys.argv[1])          # template .potx
OUT = Path(sys.argv[2])          # base .pptx
W = Path(sys.argv[3])            # scratch dir
TMP = W / "base_unz"
if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(TMP)

IN = 914400
def emu(x): return int(round(x * IN))

RED = "C8102E"

# ---------- content types ----------
ct = (TMP / "[Content_Types].xml").read_text(encoding="utf-8")
ct = ct.replace("presentationml.template.main+xml", "presentationml.presentation.main+xml")
ct = ct.replace(
    "</Types>",
    '<Override PartName="/ppt/slideLayouts/slideLayout47.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/></Types>',
)
(TMP / "[Content_Types].xml").write_text(ct, encoding="utf-8")

# ---------- new layout ----------
TITLE_X, TITLE_Y, TITLE_W, TITLE_H = emu(0.84), emu(0.30), emu(12.0), emu(0.84)
SUB_Y, SUB_H = emu(1.17), emu(0.34)
NOTE_Y, NOTE_H = emu(6.00), emu(0.84)
RULE_Y = emu(6.90)
SRC_Y, SRC_H = emu(6.96), emu(0.34)
SLIDE_W = 12192000
RIGHT = SLIDE_W - emu(0.5)
DASH_Y = TITLE_Y + emu(0.05) + emu(0.155)

def run_props(sz, bold=False, color="000000", face="Lato", extra=""):
    b = ' b="1"' if bold else ' b="0"'
    return (f'<a:defRPr sz="{sz}"{b} i="0" kern="1200"{extra}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{face}"/><a:ea typeface="{face}"/><a:cs typeface="{face}"/></a:defRPr>')

layout = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" preserve="1" userDrawn="1"><p:cSld name="NU chart slide"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="2" name="Red dash"/><p:cNvCxnSpPr/><p:nvPr userDrawn="1"/></p:nvCxnSpPr><p:spPr><a:xfrm><a:off x="0" y="{DASH_Y}"/><a:ext cx="{emu(0.56)}" cy="0"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="25400" cap="flat"><a:solidFill><a:srgbClr val="{RED}"/></a:solidFill><a:prstDash val="solid"/></a:ln></p:spPr></p:cxnSp>
<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="3" name="Footer rule"/><p:cNvCxnSpPr/><p:nvPr userDrawn="1"/></p:nvCxnSpPr><p:spPr><a:xfrm><a:off x="{TITLE_X}" y="{RULE_Y}"/><a:ext cx="{RIGHT - TITLE_X}" cy="0"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="9525" cap="flat"><a:solidFill><a:srgbClr val="000000"/></a:solidFill><a:prstDash val="solid"/></a:ln></p:spPr></p:cxnSp>
<p:sp><p:nvSpPr><p:cNvPr id="4" name="Title 1"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="{TITLE_X}" y="{TITLE_Y}"/><a:ext cx="{TITLE_W}" cy="{TITLE_H}"/></a:xfrm></p:spPr><p:txBody><a:bodyPr vert="horz" lIns="0" tIns="45720" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle><a:lvl1pPr algn="l"><a:lnSpc><a:spcPct val="92000"/></a:lnSpc>{run_props(2400, True)}</a:lvl1pPr></a:lstStyle><a:p><a:r><a:rPr lang="en-US"/><a:t>Click to edit title</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="5" name="Subtitle 2"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" sz="quarter" idx="13" hasCustomPrompt="1"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="{TITLE_X}" y="{SUB_Y}"/><a:ext cx="{TITLE_W}" cy="{SUB_H}"/></a:xfrm></p:spPr><p:txBody><a:bodyPr vert="horz" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle><a:lvl1pPr marL="0" indent="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:buNone/>{run_props(1400, False, "3A3A3F", "Lato Light")}</a:lvl1pPr></a:lstStyle><a:p><a:pPr lvl="0"/><a:r><a:rPr lang="en-US"/><a:t>Subtitle</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="6" name="Footnotes 3"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" sz="quarter" idx="14" hasCustomPrompt="1"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="{TITLE_X}" y="{NOTE_Y}"/><a:ext cx="{emu(11.5)}" cy="{NOTE_H}"/></a:xfrm></p:spPr><p:txBody><a:bodyPr vert="horz" lIns="0" tIns="0" rIns="0" bIns="0" anchor="b"><a:noAutofit/></a:bodyPr><a:lstStyle><a:lvl1pPr marL="0" indent="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:buNone/>{run_props(800, False, "3A3A3F", "Lato")}</a:lvl1pPr></a:lstStyle><a:p><a:pPr lvl="0"/><a:r><a:rPr lang="en-US"/><a:t>Footnotes and notes</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="8" name="Source 4"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" sz="quarter" idx="15" hasCustomPrompt="1"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="{TITLE_X}" y="{SRC_Y}"/><a:ext cx="{emu(9.6)}" cy="{SRC_H}"/></a:xfrm></p:spPr><p:txBody><a:bodyPr vert="horz" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle><a:lvl1pPr marL="0" indent="0" algn="l"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:buNone/>{run_props(800, False, "3A3A3F", "Lato")}</a:lvl1pPr></a:lstStyle><a:p><a:pPr lvl="0"/><a:r><a:rPr lang="en-US"/><a:t>Source</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="7" name="Northeastern University footer"/><p:cNvSpPr txBox="1"/><p:nvPr userDrawn="1"/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{RIGHT - emu(2.3)}" y="{SRC_Y}"/><a:ext cx="{emu(2.3)}" cy="{SRC_H}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="r"/><a:r><a:rPr lang="en-US" sz="900" b="1"><a:solidFill><a:srgbClr val="000000"/></a:solidFill><a:latin typeface="Lato"/><a:ea typeface="Lato"/><a:cs typeface="Lato"/></a:rPr><a:t>Northeastern University</a:t></a:r></a:p></p:txBody></p:sp>
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''
(TMP / "ppt/slideLayouts/slideLayout47.xml").write_text(layout, encoding="utf-8")
(TMP / "ppt/slideLayouts/_rels/slideLayout47.xml.rels").write_text(
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
    '</Relationships>', encoding="utf-8")

# ---------- register layout in master ----------
mrels = (TMP / "ppt/slideMasters/_rels/slideMaster1.xml.rels").read_text(encoding="utf-8")
mrels = mrels.replace(
    "</Relationships>",
    '<Relationship Id="rId99" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout47.xml"/></Relationships>')
(TMP / "ppt/slideMasters/_rels/slideMaster1.xml.rels").write_text(mrels, encoding="utf-8")
m = (TMP / "ppt/slideMasters/slideMaster1.xml").read_text(encoding="utf-8")
ids = [int(x) for x in re.findall(r'<p:sldLayoutId id="(\d+)"', m)]
pres = (TMP / "ppt/presentation.xml").read_text(encoding="utf-8")
ids += [int(x) for x in re.findall(r'<p:sldMasterId id="(\d+)"', pres)]
new_id = max(ids) + 1
m = m.replace("</p:sldLayoutIdLst>", f'<p:sldLayoutId id="{new_id}" r:id="rId99"/></p:sldLayoutIdLst>')
(TMP / "ppt/slideMasters/slideMaster1.xml").write_text(m, encoding="utf-8")

# ---------- theme palette ----------
th = (TMP / "ppt/theme/theme1.xml").read_text(encoding="utf-8")
swap = {
    "dk2": "3A3A3F", "lt2": "F4F4F5",
    "accent1": RED, "accent2": "000000", "accent3": "8A8D8F",
    "accent4": "3A3A3F", "accent5": "A4804A", "accent6": "F4F4F5",
    "hlink": "0C3354", "folHlink": "6B6B70",
}
for tag, val in swap.items():
    th, n = re.subn(rf'(<a:{tag}>)<a:srgbClr val="[0-9A-Fa-f]{{6}}"/>(</a:{tag}>)', rf'\g<1><a:srgbClr val="{val}"/>\g<2>', th)
    assert n == 1, tag
th = re.sub(r'<a:clrScheme name="[^"]*"', '<a:clrScheme name="Northeastern"', th, count=1)
(TMP / "ppt/theme/theme1.xml").write_text(th, encoding="utf-8")

# ---------- docProps ----------
rels = (TMP / "_rels/.rels").read_text(encoding="utf-8")
rels = re.sub(r'<Relationship [^>]*thumbnail[^>]*/>', '', rels)
(TMP / "_rels/.rels").write_text(rels, encoding="utf-8")
if (TMP / "docProps/thumbnail.jpeg").exists():
    (TMP / "docProps/thumbnail.jpeg").unlink()
(TMP / "docProps/app.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
    'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
    '<TotalTime>0</TotalTime><Application>Microsoft Office PowerPoint</Application>'
    '<PresentationFormat>Widescreen</PresentationFormat><Company>Northeastern University</Company></Properties>',
    encoding="utf-8")

# ---------- zip ----------
if OUT.exists():
    OUT.unlink()
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zo:
    # content types first
    zo.write(TMP / "[Content_Types].xml", "[Content_Types].xml")
    for p in sorted(TMP.rglob("*")):
        if p.is_file() and p.name != "[Content_Types].xml":
            zo.write(p, p.relative_to(TMP).as_posix())
print("wrote", OUT, OUT.stat().st_size)
