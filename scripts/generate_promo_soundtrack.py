#!/usr/bin/env python3
"""Create an original, royalty-free electronic promo soundtrack with stdlib only.

No API keys, external music files, or third-party dependencies required.
This is a self-contained short ad bed, not a copyrighted song.
"""
from __future__ import annotations

import argparse
import math
import random
import struct
import wave
from array import array
from pathlib import Path

RATE = 32000
BPM = 120
BEAT = 60 / BPM
PI = math.pi
CHORDS = [
    (130.81, 155.56, 196.00),  # Cm
    (103.83, 130.81, 155.56),  # Ab
    (155.56, 196.00, 233.08),  # Eb
    (116.54, 146.83, 174.61),  # Bb
]


def create_music(duration: float, output: Path) -> None:
    count = int(RATE * duration)
    mix = array("f", [0.0]) * count
    rng = random.Random(20261101)

    def tone(start: float, length: float, hz: float, level: float, kind: str) -> None:
        i0 = max(0, int(start * RATE))
        i1 = min(count, int((start + length) * RATE))
        for i in range(i0, i1):
            t = i / RATE - start
            if kind == "pad":
                env = min(1.0, t / 0.22) * min(1.0, (length - t) / 0.32)
                oscillator = (math.sin(2 * PI * hz * t) + 0.25 * math.sin(2 * PI * hz * 2.002 * t))
            elif kind == "pluck":
                env = (1 - math.exp(-55 * t)) * math.exp(-8.0 * t)
                oscillator = math.sin(2 * PI * hz * t) + 0.26 * math.sin(2 * PI * hz * 2 * t)
            else:  # warm bass
                env = (1 - math.exp(-70 * t)) * math.exp(-6.0 * t)
                oscillator = math.sin(2 * PI * hz * t) + 0.18 * math.sin(2 * PI * hz * 2 * t)
            mix[i] += level * env * oscillator

    def kick(start: float) -> None:
        i0 = int(start * RATE)
        for k in range(int(0.23 * RATE)):
            i = i0 + k
            if i >= count:
                break
            t = k / RATE
            phase = 2 * PI * (52 * t + 65 * (1 - math.exp(-24 * t)) / 24)
            mix[i] += 0.34 * math.sin(phase) * math.exp(-19 * t)

    def snare(start: float) -> None:
        i0 = int(start * RATE)
        previous = 0.0
        for k in range(int(0.16 * RATE)):
            i = i0 + k
            if i >= count:
                break
            t = k / RATE
            noise = rng.uniform(-1, 1)
            high = noise - previous * 0.8
            previous = noise
            mix[i] += 0.10 * high * math.exp(-22 * t)
            mix[i] += 0.06 * math.sin(2 * PI * 175 * t) * math.exp(-25 * t)

    def hat(start: float, accent: bool) -> None:
        i0 = int(start * RATE)
        prev = 0.0
        for k in range(int(0.065 * RATE)):
            i = i0 + k
            if i >= count:
                break
            t = k / RATE
            noise = rng.uniform(-1, 1)
            high = noise - prev
            prev = noise
            mix[i] += (0.033 if accent else 0.021) * high * math.exp(-55 * t)

    bars = math.ceil(duration / (4 * BEAT))
    for bar in range(bars):
        start = bar * 4 * BEAT
        root, third, fifth = CHORDS[bar % len(CHORDS)]
        for hz in (root, third, fifth):
            tone(start, min(2.15, max(0.01, duration - start)), hz * 2, 0.028, "pad")
        for beat in range(4):
            at = start + beat * BEAT
            if at >= duration:
                continue
            kick(at)
            if beat in (1, 3):
                snare(at)
            tone(at, 0.33, root / 2, 0.13, "bass")
        notes = [root * 4, third * 4, fifth * 4, third * 4,
                 root * 4, fifth * 4, third * 4, fifth * 4]
        for step, hz in enumerate(notes):
            at = start + step * BEAT / 2
            if at < duration:
                tone(at, 0.30, hz, 0.055, "pluck")
                hat(at, step % 2 == 0)

    peak = max(max(mix), -min(mix), 1e-6)
    output.parent.mkdir(parents=True, exist_ok=True)
    pcm = bytearray(count * 2)
    for i, val in enumerate(mix):
        t = i / RATE
        fade_in = min(1.0, t / 0.20)
        fade_out = min(1.0, (duration - t) / 0.75)
        sample = math.tanh((val / peak) * 1.2) * 0.83 * max(0, fade_in * fade_out)
        struct.pack_into("<h", pcm, 2 * i, int(32767 * sample))
    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm)
    print(f"Created original soundtrack: {output} ({duration:.2f}s, {RATE} Hz)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 0.5 <= args.duration <= 3600:
        parser.error("Duration must be between 0.5 and 3600 seconds")
    create_music(args.duration, args.output)
