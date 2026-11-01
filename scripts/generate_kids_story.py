#!/usr/bin/env python3
"""Free Greek dialogue + original gentle instrumental music for KidsGarden.

Uses the open-source espeak-ng Greek voice. No API keys or copyrighted tracks.
Emits audio, a synced scene timeline, and two distinct character voice pitches.
"""
from __future__ import annotations

import array
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

RATE = 32000
FPS = 24
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "remotion-composer" / "public" / "kids-story"

LINES = [
    ("sun", "Καλημέρα μικροί μου φίλοι! Είμαι ο Ήλιος.", 60, 128),
    ("flower", "Καλημέρα Ήλιε! Είμαι η Μίνα. Διψάω λιγάκι!", 83, 133),
    ("cloud", "Γεια σας! Είμαι ο Λούλης, το συννεφάκι. Μπορώ να βοηθήσω!", 40, 122),
    ("flower", "Αλήθεια, Λούλη; Έχεις λίγο νεράκι;", 84, 136),
    ("cloud", "Φυσικά! Πλιτς, πλατς, πλατς! Να οι σταγονίτσες!", 44, 126),
    ("flower", "Ααα! Τι όμορφα! Τώρα είμαι χαρούμενη!", 85, 130),
    ("sun", "Μπράβο, Λούλη! Η καλοσύνη κάνει τον κόσμο πιο όμορφο!", 61, 126),
    ("cloud", "Ας μετρήσουμε όλοι μαζί! Ένα, δύο, τρία!", 42, 132),
    ("flower", "Χαμογελάμε! Και μοιράζουμε αγάπη!", 84, 129),
]


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def save_wav(path: Path, samples: array.array) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(samples.tobytes())


def load_pcm(path: Path) -> array.array:
    with wave.open(str(path), "rb") as audio:
        if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or audio.getframerate() != RATE:
            raise RuntimeError("Unexpected WAV format: " + str(path))
        data = array.array("h")
        data.frombytes(audio.readframes(audio.getnframes()))
        if sys.byteorder != "little":
            data.byteswap()
        return data


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    timeline: list[dict[str, object]] = []
    voice_parts: list[tuple[int, array.array]] = []
    position = 2.0

    for i, (speaker, text, pitch, speed) in enumerate(LINES):
        raw = OUT / f"raw-{i + 1:02d}.wav"
        ready = OUT / f"line-{i + 1:02d}.wav"
        run(["espeak-ng", "-v", "el", "-p", str(pitch), "-s", str(speed),
             "-a", "175", "-w", str(raw), text])
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-i", str(raw), "-ar", str(RATE), "-ac", "1", "-c:a", "pcm_s16le", str(ready)])
        raw.unlink()
        samples = load_pcm(ready)
        duration = len(samples) / RATE
        start = round(position * FPS) / FPS
        voice_parts.append((round(start * RATE), samples))
        timeline.append({
            "speaker": speaker,
            "text": text,
            "start": round(start, 3),
            "duration": round(duration + 0.12, 3),
        })
        position = start + duration + 0.70

    total = math.ceil((position + 2.1) * FPS) / FPS
    count = math.ceil(total * RATE)
    dialogue = array.array("f", [0.0]) * count
    for offset, samples in voice_parts:
        for j, sample in enumerate(samples):
            if offset + j < count:
                dialogue[offset + j] += sample * 0.97

    voice_pcm = array.array("h", (max(-32768, min(32767, round(v))) for v in dialogue))
    save_wav(OUT / "dialogue.wav", voice_pcm)

    # Soft pentatonic music box + warm pad; created from math waves, fully original.
    music = array.array("f", [0.0]) * count
    melody = [392.0, 440.0, 523.25, 440.0, 392.0, 329.63, 349.23, 392.0]
    beat = 0.57
    for step in range(math.ceil(total / beat)):
        at = step * beat
        note = melody[step % len(melody)]
        start_sample = round(at * RATE)
        for k in range(int(beat * RATE * 0.9)):
            idx = start_sample + k
            if idx >= count:
                break
            t = k / RATE
            env = (1 - math.exp(-40 * t)) * math.exp(-7 * t)
            sparkle = math.sin(2 * math.pi * note * t) + 0.28 * math.sin(4 * math.pi * note * t)
            music[idx] += 0.34 * env * sparkle

    for start in range(0, math.ceil(total), 4):
        notes = [261.63, 329.63, 392.0] if (start // 4) % 2 == 0 else [220.0, 293.66, 349.23]
        for note in notes:
            origin = start * RATE
            for k in range(min(int(3.6 * RATE), count - origin)):
                t = k / RATE
                env = min(1, t * 3) * min(1, max(0, 3.6 - t) * 2)
                music[origin + k] += 0.028 * env * math.sin(2 * math.pi * note * t)

    maxval = max(0.2, max(abs(x) for x in music))
    pcm = array.array("h")
    for i, val in enumerate(music):
        t = i / RATE
        fade = min(1, t / 1.0, max(0, (total - t) / 1.2))
        pcm.append(round(max(-1, min(1, val / maxval * 0.78 * fade)) * 32000))
    save_wav(OUT / "music.wav", pcm)

    (OUT / "timeline.json").write_text(
        json.dumps({"dialogue": timeline, "duration": total}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Greek voice lines: {len(timeline)}")
    print(f"Total video duration: {total:.2f}s")
    print(f"Dialogue / music / timeline saved in {OUT}")


if __name__ == "__main__":
    main()
