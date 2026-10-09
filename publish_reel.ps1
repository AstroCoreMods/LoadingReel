# Kerbal Brains Mods loading reel: rebuild reel.cfg from this folder and push it online.
# Every Kerbal Brains mod reads reel.cfg when the game starts, so new pictures and ads show up
# in players' loading screens without a mod update.
#
#   ads\ad__<Assembly>__<name>.jpg   an ad, shown to players who do NOT have that mod yet
#   pics\<Assembly>__<name>.jpg      a loading picture, shown to players who DO have that mod
#   pics\all__<name>.jpg             a loading picture everyone sees
#   tips\<Assembly>.txt              loading tips for that mod, one per line (all.txt = everyone)
#   news\news__<name>.jpg            an ANNOUNCEMENT everyone sees: it opens the loading slideshow and comes back
#   news\news__<name>__until-YYYY-MM-DD.jpg   ...and stops showing after that date
#                                    (make one with make_announcement.py: headline, text, QR link)
#
# Assembly names: KerbalBrains, IronRoot, KerbalJumpGate, KerbalGlowUp, HullWorks, KerbalCritters, BadgeBar
# Pictures: 1920x1080 JPG, under 1 MB is best (players download them).
#
# Usage:  powershell -ExecutionPolicy Bypass -File .\publish_reel.ps1            (build + push)
#         powershell -ExecutionPolicy Bypass -File .\publish_reel.ps1 -NoPush    (build only)
param(
    [double]$AdSeconds = 8,     # how long an ad stays on screen
    [int]$AdEvery = 3,          # one ad, then (AdEvery - 1) pictures
    [double]$OurShare = 0.4,    # share of picture slots that use our pictures (the rest are the game's / JNSQ's)
    [double]$NewsSeconds = 8,   # how long an announcement stays on screen
    [int]$NewsShows = 3,        # how many times each announcement plays per loading screen
    [switch]$NoPush
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Rev($path) { (Get-FileHash $path -Algorithm SHA1).Hash.Substring(0, 8).ToLower() }
function Bad($name) { $name -notmatch '^[A-Za-z0-9_.-]{1,80}$' }

$out = New-Object System.Collections.Generic.List[string]
$out.Add("// Kerbal Brains Mods loading reel. Built by publish_reel.ps1 on $(Get-Date -Format 'yyyy-MM-dd HH:mm'). Don't edit by hand.")
$out.Add("REEL")
$out.Add("{")
$out.Add("`tadSeconds = $AdSeconds")
$out.Add("`tadEvery = $AdEvery")
$out.Add("`tourShare = $OurShare")
$out.Add("`tnewsSeconds = $NewsSeconds")
$out.Add("`tnewsShows = $NewsShows")
$n = 0

foreach ($f in Get-ChildItem ads -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png)$' }) {
    if ((Bad $f.Name) -or $f.BaseName -notmatch '^ad__([A-Za-z0-9]+)(__|$)') { Write-Warning "skipped $($f.Name) (name it ad__<Assembly>__<name>.jpg)"; continue }
    $out.Add("`tITEM"); $out.Add("`t{")
    $out.Add("`t`tfile = ads/$($f.Name)"); $out.Add("`t`tkind = ad"); $out.Add("`t`tmod = $($Matches[1])"); $out.Add("`t`trev = $(Rev $f.FullName)")
    $out.Add("`t}"); $n++
    if ($f.Length -gt 1.5MB) { Write-Warning "$($f.Name) is $([math]::Round($f.Length/1MB,1)) MB, try to keep pictures under 1 MB" }
}
foreach ($f in Get-ChildItem pics -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png)$' }) {
    if ((Bad $f.Name) -or $f.BaseName -notmatch '^([A-Za-z0-9]+)__') { Write-Warning "skipped $($f.Name) (name it <Assembly>__<name>.jpg or all__<name>.jpg)"; continue }
    $mod = if ($Matches[1] -eq "all") { "*" } else { $Matches[1] }
    $out.Add("`tITEM"); $out.Add("`t{")
    $out.Add("`t`tfile = pics/$($f.Name)"); $out.Add("`t`tkind = pic"); $out.Add("`t`tmod = $mod"); $out.Add("`t`trev = $(Rev $f.FullName)")
    $out.Add("`t}"); $n++
}
$news = 0
foreach ($f in Get-ChildItem news -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png)$' }) {
    if ((Bad $f.Name) -or $f.BaseName -notmatch '^news__([A-Za-z0-9-]+?)(?:__until-(\d{4}-\d{2}-\d{2}))?$') { Write-Warning "skipped $($f.Name) (name it news__<name>.jpg or news__<name>__until-YYYY-MM-DD.jpg)"; continue }
    $until = $Matches[2]
    if ($until -and ([datetime]::ParseExact($until, 'yyyy-MM-dd', $null)) -lt (Get-Date).Date) {
        New-Item -ItemType Directory -Force news\old | Out-Null
        Move-Item $f.FullName news\old -Force
        Write-Host "retired $($f.Name) (ended $until, moved to news\old)"; continue
    }
    $out.Add("`tITEM"); $out.Add("`t{")
    $out.Add("`t`tfile = news/$($f.Name)"); $out.Add("`t`tkind = news"); $out.Add("`t`tmod = *"); $out.Add("`t`trev = $(Rev $f.FullName)")
    if ($until) { $out.Add("`t`tuntil = $until") }
    $out.Add("`t}"); $n++; $news++
}
$t = 0
foreach ($f in Get-ChildItem tips -File -Filter *.txt -ErrorAction SilentlyContinue) {
    $mod = if ($f.BaseName -eq "all") { "*" } else { $f.BaseName }
    foreach ($line in Get-Content $f.FullName) {
        $line = $line.Trim() -replace '[{}=/]', ' '
        if ($line.Length -eq 0) { continue }
        $out.Add("`tTIP"); $out.Add("`t{"); $out.Add("`t`tmod = $mod"); $out.Add("`t`ttext = $line"); $out.Add("`t}"); $t++
    }
}
$out.Add("}")
[System.IO.File]::WriteAllLines((Join-Path $PSScriptRoot "reel.cfg"), $out, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "reel.cfg: $n pictures/ads/announcements ($news announcements), $t tips"

if (-not $NoPush) {
    git add -A
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) { git commit -m "Update loading reel ($n pictures/ads, $t tips)"; git push }
    else { Write-Host "Nothing changed." }
}
