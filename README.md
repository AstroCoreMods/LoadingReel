# Kerbal Brains Mods: Loading Reel

The loading-screen slideshow for every Kerbal Brains mod (Kerbal Brains, IronRoot, Jump Gate, HullWorks, Glow-Up, Kerbal Critters).

When the game starts, the mods read `reel.cfg` from here and download any new pictures, ads and tips. New items show up in the loading screen without a mod update.

- **Pictures** of a mod show when you have that mod.
- **Ads** for a mod show when you don't have it yet. Each ad stays up 8 seconds.
- Downloads are saved in `Kerbal Space Program/KerbalBrainsMods/LoadingReel`.
- To stay offline: open `Kerbal Space Program/KerbalBrainsMods/LoadingReel.cfg` and set `online = false`.

## Adding something
1. Drop the file in the right folder:
   - `ads/ad__<Assembly>__<name>.jpg` (an ad)
   - `pics/<Assembly>__<name>.jpg` or `pics/all__<name>.jpg` (a loading picture)
   - `tips/<Assembly>.txt` or `tips/all.txt` (one tip per line)
2. Run `publish_reel.ps1`. It rebuilds `reel.cfg` and pushes it.

Assembly names: KerbalBrains, IronRoot, KerbalJumpGate, KerbalGlowUp, HullWorks, KerbalCritters, BadgeBar.
Pictures: 1920x1080 JPG, under 1 MB.

## Announcements (reel v3)
Announcement slides go to every player with any Kerbal Brains mod. They open the loading slideshow, stay up 8 seconds and come back up to 3 times per load (several announcements take turns).

1. Make the slide:
   `python make_announcement.py --headline "IronRoot 0.9 is here" --text "Line one|Line two" --link "https://..." --tag "NEW UPDATE" --until 2026-11-15`
   (`--tag`: ANNOUNCEMENT, COMING SOON, NEW UPDATE, NEW MOD, EVENT. `--until` = last day it shows. `--link` adds a QR code.)
2. Run `publish_reel.ps1`. Expired announcements move to `news\old` by themselves.

File names: `news\news__<name>.jpg` or `news\news__<name>__until-YYYY-MM-DD.jpg`.
