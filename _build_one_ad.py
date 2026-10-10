"""Rebuild ONE loading-screen ad. Usage: python _build_one_ad.py KerbalDyson"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
which = sys.argv[1]
sys.argv = ["build_ads.py", str(HERE / "source/art"), str(HERE.parent / "_scratch/adbadges"),
            str(HERE / "source/fonts/Orbitron.ttf"), str(HERE / "ads")]
src = (HERE / "build_ads.py").read_text(encoding="utf-8").replace('if __name__ == "__main__":', "if False:")
exec(compile(src, "build_ads.py", "exec"))
for ad in ADS:
    if ad["asm"] == which:
        build(ad)
        print("rebuilt", which)
