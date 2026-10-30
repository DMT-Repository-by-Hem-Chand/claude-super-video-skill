"""Environment check for the super-video skill.

Reports what is installed and what each missing piece costs you. Changes nothing.

Usage:
    python helpers/doctor.py
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def version(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    line = (out.stdout or out.stderr).strip().splitlines()
    return line[0][:80] if line else None


def has_key(name: str) -> bool:
    if os.environ.get(name):
        return True
    for env in [SKILL_DIR / ".env", SKILL_DIR.parent.parent / ".env", Path(".env")]:
        if env.exists():
            for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
                k, _, v = line.partition("=")
                if k.strip() == name and v.strip().strip("'\""):
                    return True
    return False


def main() -> None:
    rows: list[tuple[str, bool, str]] = []

    for tool, need in [("ffmpeg", "required"), ("ffprobe", "required"),
                       ("node", "Remotion / HyperFrames (Node 22+ for HyperFrames)"),
                       ("npx", "Remotion / HyperFrames"), ("uv", "optional, faster Python installs"),
                       ("yt-dlp", "optional, download online sources")]:
        path = shutil.which(tool)
        rows.append((tool, bool(path), (version([path, "-version" if tool.startswith("ff") else "--version"]) or "ok") if path else need))

    for mod, need in [("requests", "required (Scribe)"), ("numpy", "required"), ("PIL", "required (pillow)"),
                      ("librosa", "required (waveforms)"), ("matplotlib", "required (timeline_view)"),
                      ("faster_whisper", "optional, local transcription without an API key"),
                      ("moviepy", "optional engine"), ("manim", "optional engine")]:
        ok = importlib.util.find_spec(mod) is not None
        rows.append((f"py:{mod}", ok, "ok" if ok else need))

    key = has_key("ELEVENLABS_API_KEY")
    rows.append(("ELEVENLABS_API_KEY", key,
                 "set (Scribe transcription + TTS)" if key else
                 "missing - transcription falls back to local faster-whisper"))

    width = max(len(r[0]) for r in rows)
    print(f"super-video doctor  (python {sys.version.split()[0]}, skill at {SKILL_DIR})\n")
    for name, ok, note in rows:
        print(f"  {'OK ' if ok else '-- '} {name.ljust(width)}  {note}")

    hard = [r[0] for r in rows if not r[1] and ("required" in r[2])]
    print()
    if hard:
        print("Missing required: " + ", ".join(hard))
        print("  Python deps: uv pip install -r requirements.txt   (or pip install -r requirements.txt)")
        print("  ffmpeg: winget install Gyan.FFmpeg | brew install ffmpeg | apt install ffmpeg")
        sys.exit(1)
    print("Ready.")


if __name__ == "__main__":
    main()
