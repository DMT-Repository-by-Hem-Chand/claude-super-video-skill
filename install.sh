#!/usr/bin/env sh
# Link the skill into Claude Code and install Python deps.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.claude/skills"
ln -sfn "$HERE/skills/super-video" "$HOME/.claude/skills/super-video"
if command -v uv >/dev/null; then uv pip install --system -r "$HERE/skills/super-video/requirements.txt"; else python3 -m pip install -r "$HERE/skills/super-video/requirements.txt"; fi
python3 "$HOME/.claude/skills/super-video/helpers/doctor.py" || true
echo "Installed. Restart Claude Code to load the super-video skill."
