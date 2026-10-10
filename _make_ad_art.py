"""Make ad backgrounds (source/art/0..5) from brain-crew loading pictures.
Each picture is slid right so its subject sits in the clear area on the right of the ad;
the strip uncovered on the left (hidden under the ad's dark text panel) is a blurred, dimmed copy."""
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
HERE = Path(__file__).resolve().parent
PICS = HERE.parent / "_brand" / "loading2" / "pics"
W, H = 1920, 1080
# art slot (matches build_ads.py ADS order): (picture, pixels to slide right)
JOBS = {0: ("kb2_04_cockpit", 560), 1: ("ir2_04_mine", 480), 2: ("jg2_02_warp", 520),
        3: ("gu2_01_newsuits", 220), 4: ("hw2_01_paintshop", 260), 5: ("kc2_03_icebeast", 180)}
for slot, (name, shift) in JOBS.items():
    im = Image.open(PICS / f"{name}.jpg").convert("RGB").resize((W, H))
    bg = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(40))).enhance(0.45)
    out = bg.copy()
    out.paste(im.crop((0, 0, W - shift, H)), (shift, 0))
    # soften the seam
    seam = out.crop((shift - 40, 0, shift + 40, H)).filter(ImageFilter.GaussianBlur(14))
    out.paste(seam, (shift - 40, 0))
    for old in (HERE / "source" / "art").glob(f"{slot}.*"):
        old.unlink()
    out.save(HERE / "source" / "art" / f"{slot}.jpg", quality=92)
    print("art", slot, name)
