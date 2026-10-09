"""Kerbal Brains Mods loading-screen ads.
Usage: python3 build_ads.py <art_dir> <badge_dir> <orbitron.ttf | folder with orb500/orb700/orb900.ttf> <out_dir>
art_dir: 0..5.png or .jpg (Higgsfield 16:9, text space on the left). badge_dir: <Assembly>.png round badges.
Writes ad__<Assembly>__main.jpg (1920x1080) for every mod in ADS.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ART, BADGES, FONT, OUT = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
W, H = 1920, 1080
ORANGE = (255, 140, 40); CYAN = (34, 229, 255)

ADS = [
    dict(asm="KerbalBrains", art=0, name=["KERBAL ", "BRAINS"], c=((255, 120, 200), (255, 199, 77)),
         tag="Kerbals that think for themselves",
         perks=["Kerbals walk, work and chat on their own", "A busy Space Center crew with trucks",
                "Give orders: dig, build, drive the rover"]),
    dict(asm="IronRoot", art=1, name=["IRON", "ROOT"], c=((255, 140, 40), (255, 210, 90)),
         tag="Grow. Mine. Survive.",
         perks=["Build colonies, greenhouses and habitats", "Dig ore and smelt Metal to build more",
                "Colony Express drops a colony anywhere"]),
    dict(asm="KerbalJumpGate", art=2, name=["JUMP ", "GATE"], c=((34, 229, 255), (140, 120, 255)),
         tag="Fly through the ring. Pop out at another planet.",
         perks=["Kerbin to Duna in seconds", "Build and deploy your own gates", "Gate contracts with landing bonuses"]),
    dict(asm="KerbalGlowUp", art=3, name=["GLOW", "-UP"], c=((255, 90, 200), (160, 110, 255)),
         tag="New suits, patches and Photo Mode",
         perks=["Planet suits and job colors", "Glowing helmet lights and colony patches", "Photo Mode: freeze time, pose, snap"]),
    dict(asm="HullWorks", art=4, name=["HULL", "WORKS"], c=((255, 64, 166), (255, 199, 77)),
         tag="Paint Shop for every ship",
         perks=["55 colors plus chrome and metallic", "Paint the whole ship in one click",
                "61 stickers, plus your own logos"]),
    dict(asm="KerbalCritters", art=5, name=["KERBAL ", "CRITTERS"], c=((120, 255, 140), (34, 229, 255)),
         tag="Every world has a creature waiting",
         perks=["8 critters to discover on 8 worlds", "Fill your Creature Book", "Critters roam near your lander"]),
]


WEIGHTS = {"Black": 900, "Bold": 700, "Medium": 500}


def font(px, weight="Black"):
    if Path(FONT).is_dir():     # static weights: orb500.ttf, orb700.ttf, orb900.ttf
        return ImageFont.truetype(str(Path(FONT) / f"orb{WEIGHTS.get(weight, 900)}.ttf"), px)
    f = ImageFont.truetype(FONT, px)
    try: f.set_variation_by_name(weight)
    except Exception: pass
    return f


def gradient_fill(size, c1, c2, horizontal=True):
    w, h = size
    g = Image.new("RGBA", size)
    d = ImageDraw.Draw(g)
    n = w if horizontal else h
    for i in range(n):
        t = i / max(1, n - 1)
        col = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3)) + (255,)
        if horizontal: d.line([(i, 0), (i, h)], fill=col)
        else: d.line([(0, i), (w, i)], fill=col)
    return g


def text_grad(img, xy, text, f, c1, c2):
    d = ImageDraw.Draw(img)
    bb = d.textbbox(xy, text, font=f)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).text(xy, text, font=f, fill=255)
    m = m.crop(bb)
    img.paste(gradient_fill((bb[2] - bb[0], bb[3] - bb[1]), c1, c2), (bb[0], bb[1]), m)
    return bb


def shadow_text(img, xy, text, f, blur=6, off=(3, 5), alpha=210):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + off[0], xy[1] + off[1]), text, font=f, fill=(0, 0, 0, alpha))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def build(ad):
    src = ART / f"{ad['art']}.png"
    if not src.exists(): src = ART / f"{ad['art']}.jpg"
    im = Image.open(src).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H)).convert("RGBA")

    # dark panel on the left for readable text
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
    for x in range(0, 1180):
        t = 1 - x / 1180
        sd.line([(x, 0), (x, H)], fill=(3, 6, 16, int(235 * min(1, t * 1.35) ** 1.2)))
    im.alpha_composite(shade)
    px0, py0, px1, py1 = 52, 60, 1130, 1000
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle([px0, py0, px1, py1], radius=40, fill=(4, 8, 20, 178))
    im.alpha_composite(panel.filter(ImageFilter.GaussianBlur(3)))
    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle([px0, py0, px1, py1], radius=40, outline=CYAN + (110,), width=2)
    im.alpha_composite(edge)
    d = ImageDraw.Draw(im)
    X = 96

    # ribbon
    rf = font(30, "Bold")
    rtxt = "YOU DON'T HAVE THIS ONE YET!"
    rb = d.textbbox((0, 0), rtxt, font=rf)
    rw, rh = rb[2] - rb[0] + 56, 58
    pill = Image.new("RGBA", (rw, rh), (0, 0, 0, 0))
    pm = Image.new("L", (rw * 4, rh * 4), 0); ImageDraw.Draw(pm).rounded_rectangle([0, 0, rw * 4 - 1, rh * 4 - 1], radius=rh * 2, fill=255)
    pill.paste(gradient_fill((rw, rh), (255, 120, 30), (255, 190, 60)), (0, 0), pm.resize((rw, rh), Image.LANCZOS))
    im.alpha_composite(pill, (X, 92))
    d = ImageDraw.Draw(im)
    d.text((X + 28, 92 + (rh - (rb[3] - rb[1])) // 2 - rb[1]), rtxt, font=rf, fill=(20, 12, 4))

    # badge + name
    bs = 210
    badge = Image.open(BADGES / f"{ad['asm']}.png").convert("RGBA").resize((bs, bs), Image.LANCZOS)
    by = 196
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([X - 12, by - 12, X + bs + 12, by + bs + 12], fill=ad["c"][0] + (130,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(20)))
    im.alpha_composite(badge, (X, by))

    a, b = ad["name"]
    tx, ty = X + bs + 40, by + 10
    size = 124
    while size > 60:
        nf = font(size, "Black")
        if d.textbbox((0, 0), a + b, font=nf)[2] <= 1090 - tx: break
        size -= 4
    ty += (124 - size) // 2
    shadow_text(im, (tx, ty), a + b, nf)
    d = ImageDraw.Draw(im)
    d.text((tx, ty), a, font=nf, fill=(244, 248, 255))
    adv = d.textlength(a, font=nf)
    nb = text_grad(im, (int(tx + adv + 6), ty), b, nf, *ad["c"])
    d = ImageDraw.Draw(im)
    ux0, ux1, uy = tx + 4, nb[2], nb[3] + 22
    im.alpha_composite(gradient_fill((ux1 - ux0, 5), CYAN, ORANGE), (ux0, uy))
    sf = font(36, "Medium")
    while d.textbbox((0, 0), ad["tag"], font=sf)[2] > 1090 - tx - 4: sf = font(sf.size - 2, "Medium")
    d = ImageDraw.Draw(im)
    d.text((tx + 4, uy + 22), ad["tag"], font=sf, fill=(232, 240, 250))

    # perks
    pf = font(40, "Bold")
    py = 520
    for p in ad["perks"]:
        cx, cy, r = X + 26, py + 26, 24
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CYAN)
        d.line([(cx - 11, cy + 1), (cx - 3, cy + 10), (cx + 12, cy - 9)], fill=(4, 18, 30), width=7, joint="curve")
        shadow_text(im, (X + 74, py), p, pf, blur=4, off=(2, 3), alpha=180)
        d = ImageDraw.Draw(im)
        d.text((X + 74, py), p, font=pf, fill=(246, 249, 255))
        py += 92

    # call to action: show off, never sell (no prices, tiers or memberships inside the game)
    cf = font(40, "Black")
    ctxt = "ANOTHER KERBAL BRAINS MOD"
    cb = d.textbbox((0, 0), ctxt, font=cf)
    cw, ch = cb[2] - cb[0] + 80, 92
    cy0 = 850
    btn = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    bm = Image.new("L", (cw * 4, ch * 4), 0); ImageDraw.Draw(bm).rounded_rectangle([0, 0, cw * 4 - 1, ch * 4 - 1], radius=ch * 2, fill=255)
    bglow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(bglow).rounded_rectangle([X - 8, cy0 - 8, X + cw + 8, cy0 + ch + 8], radius=ch, fill=(255, 95, 168, 140))
    im.alpha_composite(bglow.filter(ImageFilter.GaussianBlur(16)))
    btn.paste(gradient_fill((cw, ch), (255, 184, 214), (255, 120, 200)), (0, 0), bm.resize((cw, ch), Image.LANCZOS))
    im.alpha_composite(btn, (X, cy0))
    d = ImageDraw.Draw(im)
    d.text((X + 40, cy0 + (ch - (cb[3] - cb[1])) // 2 - cb[1]), ctxt, font=cf, fill=(74, 13, 42))

    im.convert("RGB").save(OUT / f"ad__{ad['asm']}__main.jpg", quality=88, optimize=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for ad in ADS: build(ad)
    print("ads:", len(ADS))
