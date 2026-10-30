# Link the skill into Claude Code (junction, no admin needed) and install Python deps.
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "skills\super-video"
$skills = Join-Path $HOME ".claude\skills"
$dst = Join-Path $skills "super-video"
New-Item -ItemType Directory -Force $skills | Out-Null
if (Test-Path $dst) { (Get-Item $dst).Delete() }
New-Item -ItemType Junction -Path $dst -Target $src | Out-Null
$req = Join-Path $src "requirements.txt"
if (Get-Command uv -ErrorAction SilentlyContinue) { uv pip install --system -r $req } else { python -m pip install -r $req }
python (Join-Path $dst "helpers\doctor.py")
Write-Host "Installed. Restart Claude Code to load the super-video skill."
