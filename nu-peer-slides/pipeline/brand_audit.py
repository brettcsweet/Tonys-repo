import sys, zipfile, re
from collections import Counter
z = zipfile.ZipFile(sys.argv[1])
ALLOWED = {"C8102E":"Northeastern Red","000000":"Black","FFFFFF":"White","3A3A3F":"Graphite","8A8D8F":"Husky Grey","6B6B70":"Muted",
           "0C3354":"Navy (NU template theme; private institutions per Brett)","8FA9F5":"Light royal blue tint (slide 3 estimated health-system markers, requested by Brett)","1F4FE0":"Royal blue (slide 1 private markers and slide 3 health-system markers, requested by Brett; not an NU brand color)","E4E4E6":"light gridline grey","D9D9DB":"light gridline grey","C9C9CC":"row-line grey"}
cols, fonts, geoms = Counter(), Counter(), Counter()
scheme = Counter()
for n in z.namelist():
    if re.match(r"ppt/(slides|charts)/[^/]+\.xml$", n) or n == "ppt/slideLayouts/slideLayout47.xml":
        t = z.read(n).decode("utf-8", "ignore")
        cols.update(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', t))
        scheme.update(re.findall(r'schemeClr val="(\w+)"', t))
        fonts.update(re.findall(r'typeface="([^"]+)"', t))
        geoms.update(re.findall(r'prst="(\w+)"', t))
print("colors used:")
for c, n in cols.most_common():
    print(f"  {c.upper()}  x{n:<5} {'OK  ' + ALLOWED[c.upper()] if c.upper() in ALLOWED else '*** NOT IN PALETTE ***'}")
print("scheme colors used in slides/charts:", dict(scheme))
print("typefaces:", dict(fonts))
print("shape geometries:", dict(geoms), "| rounded:", [g for g in geoms if 'round' in g.lower()])
th = z.read("ppt/theme/theme1.xml").decode()
print("theme accents:", re.findall(r'<a:(accent\d|dk2|lt2|hlink)><a:srgbClr val="(\w+)"', th))
bad_fonts = [f for f in fonts if f not in ("Lato", "Lato Light", "+mn-lt", "+mj-lt", "+mn-ea", "+mj-ea", "+mn-cs", "+mj-cs")]
print("non-Lato typefaces:", bad_fonts)
