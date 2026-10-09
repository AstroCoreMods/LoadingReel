"""Kerbal Brains Mods loading-screen ANNOUNCEMENT slide (1920x1080) with a QR code.

Example:
  python make_announcement.py --headline "IronRoot 0.9 is here" ^
      --text "Walk-in mines and new smelters|Your colonies grow while you fly" ^
      --link "https://example.com/ironroot" --label "kerbalbrains.example/ironroot" ^
      --tag "NEW UPDATE" --until 2026-11-15

Writes news/news__<name>[__until-YYYY-MM-DD].jpg. Then run publish_reel.ps1 to send it to every player.
Options:
  --headline   big title (1 or 2 lines, auto-sized)
  --text       up to 3 short lines, separated by |
  --link       where the QR code goes (leave out for no QR)
  --label      short link text printed under the QR (defaults to the link without https://)
  --tag        ribbon text: ANNOUNCEMENT, COMING SOON, NEW UPDATE, NEW MOD, EVENT ... (default ANNOUNCEMENT)
  --until      last day to show it (YYYY-MM-DD); leave out to show until you delete it
  --art        background picture (16:9). Default: a random one from source/art
  --name       file name part (default: from the headline)
Needs: pip install pillow qrcode
"""
import argparse, random, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode

HERE = Path(__file__).resolve().parent
W, H = 1920, 1080
ORANGE = (255, 140, 40); CYAN = (34, 229, 255); PINK = (255, 120, 200)

ap = argparse.ArgumentParser()
ap.add_argument("--headline", required=True)
ap.add_argument("--text", default="")
ap.add_argument("--link", default="")
ap.add_argument("--label", default="")
ap.add_argument("--tag", default="ANNOUNCEMENT")
ap.add_argument("--until", default="")
ap.add_argument("--art", default="")
ap.add_argument("--name", default="")
ap.add_argument("--font", default="")
ap.add_argument("--out", default=str(HERE / "news"))
a = ap.parse_args()

if a.until and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.until):
    sys.exit("--until must look like 2026-11-15")

FONT = a.font or next((str(p) for p in [HERE / "source/fonts/Orbitron.ttf", HERE / "source/fonts"] if p.exists()), "")
if not FONT:
    sys.exit("No Orbitron font: put Orbitron.ttf (or orb500/orb700/orb900.ttf) in source/fonts, or pass --font")
WEIGHTS = {"Black": 900, "Bold": 700, "Medium": 500}


def font(px, weight="Black"):
    if Path(FONT).is_dir():
        return ImageFont.truetype(str(Path(FONT) / f"orb{WEIGHTS.get(weight, 900)}.ttf"), px)
    f = ImageFont.truetype(FONT, px)
    try: f.set_variation_by_name(weight)
    except Exception: pass
    return f


def grad(size, c1, c2):
    w, h = size
    g = Image.new("RGBA", size); d = ImageDraw.Draw(g)
    for i in range(w):
        t = i / max(1, w - 1)
        d.line([(i, 0), (i, h)], fill=tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3)) + (255,))
    return g


def pill(im, xy, text, f, c1, c2, ink):
    d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0] + 56, bb[3] - bb[1] + 30
    m = Image.new("L", (w * 4, h * 4), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=h * 2, fill=255)
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0)); p.paste(grad((w, h), c1, c2), (0, 0), m.resize((w, h), Image.LANCZOS))
    im.alpha_composite(p, xy)
    ImageDraw.Draw(im).text((xy[0] + 28, xy[1] + 15 - bb[1]), text, font=f, fill=ink)
    return h


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def shadow_text(im, xy, text, f, fill):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 3, xy[1] + 5), text, font=f, fill=(0, 0, 0, 200))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(im).text(xy, text, font=f, fill=fill)


# background
arts = sorted((HERE / "source/art").glob("*.*"))
art = Path(a.art) if a.art else (random.choice(arts) if arts else None)
if art:
    im = Image.open(art).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H)).convert("RGBA")
    im = im.filter(ImageFilter.GaussianBlur(2))
else:
    im = grad((W, H), (6, 10, 26), (24, 12, 40))
shade = Image.new("RGBA", (W, H), (3, 6, 16, 120)); im.alpha_composite(shade)

has_qr = bool(a.link)
px0, py0, px1, py1 = 60, 70, (1250 if has_qr else 1860), 1010
panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(panel).rounded_rectangle([px0, py0, px1, py1], radius=44, fill=(4, 8, 20, 205))
im.alpha_composite(panel.filter(ImageFilter.GaussianBlur(3)))
edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(edge).rounded_rectangle([px0, py0, px1, py1], radius=44, outline=ORANGE + (170,), width=3)
im.alpha_composite(edge)
d = ImageDraw.Draw(im)
X, maxw = 112, px1 - 112 - 52

# ribbon + eyebrow
y = 120
y += pill(im, (X, y), a.tag.upper(), font(34, "Bold"), (255, 110, 30), (255, 196, 64), (22, 12, 2)) + 26
d = ImageDraw.Draw(im)
ef = font(30, "Bold"); d.text((X, y), "KERBAL BRAINS MODS", font=ef, fill=CYAN)
y += 62

# headline: largest size that fits in 2 lines
for size in range(132, 60, -4):
    hf = font(size, "Black")
    lines = wrap(d, a.headline.upper(), hf, maxw)
    if len(lines) <= 2: break
for ln in lines:
    shadow_text(im, (X, y), ln, hf, (246, 249, 255))
    y += int(size * 1.12)
y += 6
ImageDraw.Draw(im).rectangle([X + 4, y, X + min(maxw, 640), y + 5], fill=ORANGE)
im.alpha_composite(grad((min(maxw, 640) - 4, 5), CYAN, ORANGE), (X + 4, y))
y += 40

# body lines
bf = font(44, "Medium")
d = ImageDraw.Draw(im)
for ln in [t.strip() for t in a.text.split("|") if t.strip()][:3]:
    for sub in wrap(d, ln, bf, maxw)[:2]:
        shadow_text(im, (X, y), sub, bf, (226, 234, 246))
        y += 62
    y += 10

# footer line
ff = font(28, "Medium")
foot = ("Showing until " + a.until) if a.until else ""
if foot: ImageDraw.Draw(im).text((X, py1 - 70), foot, font=ff, fill=(150, 165, 190))

# QR card
if has_qr:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(a.link); qr.make(fit=True)
    q = qr.make_image(fill_color=(10, 14, 28), back_color=(255, 255, 255)).convert("RGBA")
    qs = 440
    q = q.resize((qs, qs), Image.NEAREST)
    cx0, cy0 = 1330, 170
    cw, ch = qs + 60, qs + 190
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([cx0 - 10, cy0 - 10, cx0 + cw + 10, cy0 + ch + 10], radius=40, fill=CYAN + (120,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22)))
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + ch], radius=34, fill=(255, 255, 255, 255))
    im.alpha_composite(card)
    im.alpha_composite(q, (cx0 + 30, cy0 + 30))
    d = ImageDraw.Draw(im)
    sf = font(40, "Black"); t = "SCAN ME"
    d.text((cx0 + cw // 2 - d.textlength(t, font=sf) // 2, cy0 + qs + 52), t, font=sf, fill=(10, 14, 28))
    label = a.label or re.sub(r"^https?://(www\.)?", "", a.link).rstrip("/")
    for size in range(32, 16, -2):
        lf = font(size, "Bold")
        if d.textlength(label, font=lf) <= cw - 40: break
    d.text((cx0 + cw // 2 - d.textlength(label, font=lf) // 2, cy0 + qs + 112), label, font=lf, fill=(0, 120, 160))

name = a.name or re.sub(r"[^a-z0-9]+", "-", a.headline.lower()).strip("-")[:40]
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
fn = out / ("news__" + name + (("__until-" + a.until) if a.until else "") + ".jpg")
im.convert("RGB").save(fn, quality=88, optimize=True)
print("wrote", fn)
