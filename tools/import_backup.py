"""One-off import from the local citybike_backup: prices, products, widgets, fonts and processed photos.

Usage: python tools/import_backup.py <path to citybike_backup>
Writes data/*.json, data/calc_widget.html and docs/assets/{img,fonts}. The originals stay in the backup.
"""
import glob
import html
import json
import os
import re
import sys
import urllib.request

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

BACKUP = os.path.abspath(sys.argv[1])
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
IMG = os.path.join(HERE, "docs", "assets", "img")
FONTS = os.path.join(HERE, "docs", "assets", "fonts")
CDN = os.path.join(BACKUP, "assets", "static.tildacdn.com")
for d in (DATA, IMG, FONTS):
    os.makedirs(d, exist_ok=True)


def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def text(t):
    t = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", t, flags=re.S)
    t = re.sub(r"<(br|/div|/p|/li|/h\d)[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return [x for x in (re.sub(r"\s+", " ", l).strip() for l in t.split("\n")) if x]


# Prices: tables come through as "name; price" lines between a "...; цена" header and "Button".
TYPOS = [("Расспецовка", "Расспицовка"), ("Шипованние", "Шипование"), ("длинны", "длины"), ("трансмиссиию", "трансмиссию"), ("датчков", "датчиков"), ("выпресовка", "выпрессовка")]


def prices(page):
    groups, cur = [], None
    for line in text(read(f"{BACKUP}/public/{page}.html")):
        m = re.match(r"^(.+?)\s*;\s*цена\s*;?$", line)
        if m:
            cur = {"title": m.group(1).strip(), "rows": []}
            groups.append(cur)
        elif line == "Button":
            cur = None
        elif cur is not None and ";" in line:
            name, price = line.rstrip(";").rsplit(";", 1)
            name = name.strip().strip('"').strip()
            for a, b in TYPOS:
                name = name.replace(a, b)
            cur["rows"].append([name, price.strip()])
    return groups


all_prices = {p: prices(p) for p in ("veloservice", "electroservice")}
json.dump(all_prices, open(f"{DATA}/prices.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: (len(v), sum(len(g["rows"]) for g in v)) for k, v in all_prices.items()})


# Photos
def tinted(im, amount):
    """Crush shadows slightly toward the brand purple so mixed phone shots read as one series."""
    grey = ImageOps.grayscale(im)
    mask = grey.point(lambda v: int(max(0, 110 - v) * amount))
    return Image.composite(Image.new("RGB", im.size, (58, 0, 66)), im, mask)


def vignette(im, power):
    mask = Image.radial_gradient("L").resize(im.size).point(lambda v: int(min(255, (v / 255) ** 2.4 * 255 * power)))
    return Image.composite(Image.new("RGB", im.size, (6, 4, 10)), im, mask)


def process(src, name, widths, ratio=None, focus=(0.5, 0.5), mode="site"):
    with Image.open(src) as raw:
        im = ImageOps.exif_transpose(raw).convert("RGB")
    if ratio:
        im = ImageOps.fit(im, (int(ratio * min(im.height, im.width / ratio)), int(min(im.height, im.width / ratio))), Image.LANCZOS, centering=focus)
    im = Image.blend(im, ImageOps.autocontrast(im, cutoff=0.6), 0.55)
    if mode == "site":
        im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.2)).enhance(1.14)
        im = tinted(im, 0.55)
    elif mode == "product":
        im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.08)).enhance(1.05)
    for w in widths:
        out = im if im.width <= w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        out = out.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=3))
        if mode == "site":
            out = vignette(out, 0.42)
        out.save(os.path.join(IMG, f"{name}-{w}.webp"), "WEBP", quality=78, method=6)


sites = json.load(open(sys.argv[2], encoding="utf-8")) if len(sys.argv) > 2 else None
# name: (backup folder, wanted ratio, focus)
PICKS = {
    "neon": ("tild3630-6130-4433-b062-663261366535/Jw5DRVRO4eU.jpg", None, (0.5, 0.5)),
    "master": ("tild6635-3764-4964-b730-383938356334/_j6e81CHt6E.jpg", None, (0.5, 0.5)),
    "bench": ("tild3439-6661-4838-a433-633131656164/asd.jpg", None, (0.5, 0.5)),
    "evgeny": ("tild3035-6434-4362-a535-303037393332/ATaqwuAGmhA.jpg", None, (0.5, 0.5)),
    "truing": ("tild3761-6536-4735-b033-316439303030/photo.JPG", None, (0.5, 0.5)),
    "fat": ("tild3430-3738-4032-a437-386365646565/x4NdKMOKur0k1SIJwoSs.jpg", 4 / 3, (0.5, 0.5)),
    "motors": ("tild3562-6230-4634-b664-366439363733/gM9fQmSLlEF2-1hYRmxg.jpg", 4 / 3, (0.5, 0.5)),
    "wiring": ("tild6561-3733-4662-b636-356232386466/sVHyoHzzjLBlq06D7eV5.jpg", 4 / 3, (0.5, 0.5)),
    "kit": ("tild6663-6533-4665-b539-653838666338/5fb771ee-ec08-41cd-b.jpg", 4 / 3, (0.5, 0.5)),
    "frame-blue": ("tild3661-3736-4838-b732-376362353632/0yt96UtCBYs.jpg", 4 / 3, (0.5, 0.5)),
    "fat-orange": ("tild3136-3039-4563-a637-316364303461/u1whUYxr2NsIIgwiPvK7.jpg", 4 / 3, (0.5, 0.5)),
    "stator": ("tild3266-3562-4662-b639-363933313565/Xu4sCKi9Xy4.jpg", 4 / 3, (0.5, 0.5)),
    "hub": ("tild3262-6135-4066-b863-393663666135/8MHwROjepks.jpg", 4 / 3, (0.5, 0.5)),
    "ebike-shop": ("tild3938-6332-4338-b537-396564343461/XuYtX6dhyMySw39lhsOg.jpg", 4 / 3, (0.5, 0.5)),
    "ebike-teal": ("tild3537-6565-4561-a166-623037353636/xQYovgUs7RdSJTDFpxbO.jpg", 4 / 3, (0.5, 0.5)),
    "ebike-graffiti": ("tild3437-3665-4130-b239-343335646462/KFTkChC2t9vU-fP4b_Ea.jpg", 4 / 3, (0.5, 0.5)),
    "ebike-red": ("tild6334-6237-4163-b937-316436303034/dLr_QaoFWFY3Hqd0NXZs.jpg", 4 / 3, (0.5, 0.5)),
    "retro-pink": ("tild3530-6231-4436-b837-653039633130/O4L_KQnX50Y.jpg", 4 / 3, (0.5, 0.5)),
    "retro-red": ("tild3431-3736-4535-b930-653864303634/XhHzvF39ULTgHxYfdAfv.jpg", 4 / 3, (0.5, 0.5)),
    "retro-fold": ("tild3666-3935-4264-a235-396164363062/2kmI12ob0i4Eb4J2kngh.jpg", 4 / 3, (0.5, 0.5)),
    "groupset": ("tild6231-3661-4333-a666-376439396530/obves_s_velosipeda.jpg", 4 / 3, (0.5, 0.5)),
    "flatlay": ("tild3364-6130-4737-b266-393763666262/50332529_37019400046.jpg", 4 / 3, (0.5, 0.5)),
    "spokes": ("tild3061-3735-4533-a132-373562303766/photo.jpg", None, (0.5, 0.5)),
    "rim": ("tild3330-6338-4462-b066-653136353334/vosmerka.jpg", None, (0.5, 0.5)),
    "ekit": ("tild6636-6337-4130-a364-663934336335/i_LHfyeQ6ac.jpg", 4 / 3, (0.5, 0.5)),
    # Jenya's own shots with his marks: never cropped (ratio None), shown at natural proportions.
    "orange": ("tild3430-6432-4562-a535-656561373037/Muty1LW6MQ0.jpg", None, (0.5, 0.5)),
    "orange-brake": ("tild3634-6439-4130-a237-376237656331/LxGlhI59Erc.jpg", None, (0.5, 0.5)),
    "orange-drop": ("tild3637-6131-4632-b930-346261373865/Jmg-7k9pnDI.jpg", None, (0.5, 0.5)),
    "orange-lever": ("tild6632-3761-4335-a131-396233383939/6YmZGDJ4C2c.jpg", None, (0.5, 0.5)),
    "orange-basket": ("tild3032-6438-4030-b736-663437613234/MJbrqrw4xkU.jpg", None, (0.5, 0.5)),
    "orange-v": ("tild3437-3039-4138-b961-323238323937/RVsOoMnGquE.jpg", None, (0.5, 0.5)),
    "blue-girl": ("tild3361-3030-4739-a432-333735616434/lpF8tkUFmQw.jpg", None, (0.5, 0.5)),
    "teal-saddle": ("tild6466-6335-4434-b964-333739316433/30QtiPfhFvk.jpg", None, (0.5, 0.5)),
    "retro-blue": ("tild3437-6461-4239-a666-366337363465/noroot.png", None, (0.5, 0.5)),
}
for name, (rel, ratio, focus) in PICKS.items():
    process(os.path.join(CDN, *rel.split("/")), name, (1600, 800), ratio, focus)

# Logo mascot on transparent background, from the black logo tile.
logo_candidates = [r for r in glob.glob(CDN + "/*/*") if re.search(r"\.(png|jpe?g)$", r, re.I)]
for path in logo_candidates:
    with Image.open(path) as t:
        if t.size == (1680, 1470):
            im = t.convert("RGB")
            im.crop(im.getbbox()).save(os.path.join(IMG, "logo.webp"), "WEBP", quality=88)
            im.resize((512, 448), Image.LANCZOS).save(os.path.join(IMG, "logo-512.png"))
            s = ImageOps.fit(im, (180, 180), Image.LANCZOS, centering=(0.5, 0.35))
            s.save(os.path.join(HERE, "docs", "apple-touch-icon.png"))
            s.resize((48, 48), Image.LANCZOS).save(os.path.join(HERE, "docs", "favicon.png"))
            break

# Products
parts = {str(p["uid"]): p["title"] for p in json.loads(read(BACKUP + "/admin/store/getpartslist.json"))["parts"]}
products = []
for p in glob.glob(BACKUP + "/admin/store/products/*.json"):
    d = json.loads(read(p))
    d = d.get("product", d)
    if d.get("off") == "y":
        continue
    gal = d.get("gallery") or "[]"
    gal = json.loads(gal) if isinstance(gal, str) else gal
    imgs = []
    for n, g in enumerate(gal[:4]):
        rel = (g.get("img") or "").split("static.tildacdn.com/")[-1]
        src = os.path.join(CDN, *rel.split("/"))
        if os.path.exists(src):
            name = f"p{d['uid']}-{n}"
            process(src, name, (800,), 1.0, (0.5, 0.5), "product")
            imgs.append(name)
    products.append({
        "id": str(d["uid"]),
        "title": re.sub(r"\s+", " ", d.get("title") or "").strip(),
        "text": re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", d.get("text") or d.get("descr") or ""))).strip(),
        "price": int(float(d.get("price") or 0)),
        "old": int(float(d.get("priceold") or 0)),
        "qty": d.get("quantity") or "",
        "cats": [parts.get(x.strip(), x.strip()) for x in str(d.get("partuids") or "").strip("[]").replace('"', "").split(",") if x.strip()],
        "imgs": imgs,
        "sort": int(d.get("sort") or 0),
    })
products.sort(key=lambda x: x["sort"])
json.dump(products, open(f"{DATA}/products.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("products", len(products), "photos", sum(len(p["imgs"]) for p in products), {c for p in products for c in p["cats"]})

# Calculator: same logic and prices, admin panel and its client-side password removed.
calc = None
for r in json.loads(read(glob.glob(BACKUP + "/admin/pages/131102486_*.json")[0]))["records"]:
    m = re.search(r"<!-- nominify begin -->(.*?)<!-- nominify end -->", r.get("html") or "", re.S)
    if m:
        calc = html.unescape(m.group(1))
calc = re.sub(r"const password = prompt\([^)]*\);\s*if \(password === '[^']*'\)", "if (false)", calc)
calc = re.sub(r'<button class="admin-btn" id="adminBtn">.*?</button>', '<button class="admin-btn" id="adminBtn" hidden></button>', calc, flags=re.S)
assert "prompt(" not in calc
open(f"{DATA}/calc_widget.html", "w", encoding="utf-8").write(calc)
print("calc", len(calc))

# Diagnostic cards from the old /sovets page: real text, now indexable as plain HTML.
diag_src = ""
for r in json.loads(read(glob.glob(BACKUP + "/admin/pages/254012109_*.json")[0]))["records"]:
    m = re.search(r"<!-- nominify begin -->(.*?)<!-- nominify end -->", r.get("html") or "", re.S)
    if m and 'class="diag-card"' in html.unescape(m.group(1)):
        diag_src = html.unescape(m.group(1))
diag = []
for attrs, body in re.findall(r'<div class="diag-card" ([^>]*)>(.*?)</div>\s*</div>\s*(?=<div class="diag-card"|</div>)', diag_src + "</div>", re.S):
    sections = []
    for sec in re.findall(r'<div class="card-section[^"]*">\s*(.*?)\s*</div>', body + "</div>", re.S):
        label = re.search(r"<strong>(.*?)</strong>", sec, re.S).group(1)
        label = re.sub(r"[^\w\s(),:/-]", "", label).strip().rstrip(":")
        rest = re.sub(r"<strong>.*?</strong>", "", sec, flags=re.S)
        lines = [re.sub(r"\s+", " ", x).strip() for x in re.split(r"</?p>", rest) if x.strip()]
        sections.append({"label": label, "lines": lines})
    diag.append({"cat": re.search(r'data-cat="(\w+)"', attrs).group(1), "kw": re.search(r'data-keywords="([^"]*)"', attrs).group(1), "title": re.search(r"<h3>(.*?)</h3>", body, re.S).group(1).strip(), "sections": sections})
json.dump(diag, open(f"{DATA}/diag.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("diag cards", len(diag), [len(d["sections"]) for d in diag])

# Fonts (OFL), self-hosted so the site does not depend on Google Fonts availability.
for fam, weights in (("oswald", (500, 700)), ("manrope", (400, 600, 800))):
    for w in weights:
        for sub in ("cyrillic", "latin"):
            target = os.path.join(FONTS, f"{fam}-{sub}-{w}.woff2")
            if not os.path.exists(target):
                url = f"https://cdn.jsdelivr.net/npm/@fontsource/{fam}@5.0.0/files/{fam}-{sub}-{w}-normal.woff2"
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "citybike-build"}), timeout=30) as r:
                    open(target, "wb").write(r.read())
size = sum(os.path.getsize(p) for p in glob.glob(IMG + "/*")) / 1e6
print("images MB", round(size, 1), "files", len(os.listdir(IMG)))
