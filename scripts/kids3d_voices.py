#!/usr/bin/env python3
"""English dialogue + original music for the 3D short 'Pizza Weather'.

Uses Kokoro open-weight local TTS. All sounds are generated locally; zero paid APIs.
"""
import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

RATE = 24000
OUT = Path("kids3d-build")
OUT.mkdir(exist_ok=True)

SCRIPT = [
    ("pip", "Puff! Can you make it rain pizza?"),
    ("puff", "Pizza? Of course. I'm a professional cloud."),
    ("pip", "A professional pizza cloud?"),
    ("puff", "Stand back! Pizza storm, activate!"),
    ("pip", "Whoa! One! Two! Wait... TWENTY?!"),
    ("puff", "Uh oh. I think I ordered extra."),
    ("pip", "Best. Weather. Ever!"),
]

def main():
    pipeline = KPipeline(lang_code="a", device="cpu")
    cursor = 0.85
    parts = []
    entries = []
    for idx, (speaker, words) in enumerate(SCRIPT):
        voice = "af_heart" if speaker == "pip" else "am_michael"
        segments = []
        for _, _, sound in pipeline(words, voice=voice, speed=1.07):
            segments.append(np.asarray(sound, dtype=np.float32))
        if not segments:
            raise RuntimeError("TTS returned no audio for line " + str(idx))
        wave = np.concatenate(segments)
        wave = np.pad(wave, (0, int(RATE * 0.08)))
        start = float(cursor)
        duration = len(wave) / RATE
        parts.append((round(start * RATE), wave))
        entries.append({"speaker": speaker, "text": words, "start": round(start,3),
                        "duration": round(duration,3)})
        cursor += duration + (0.72 if idx == 3 else 0.43)
        print(speaker, repr(words), "duration", round(duration,2), flush=True)

    duration = math.ceil((cursor + 1.6) * 12) / 12
    length = int(duration * RATE)
    mix = np.zeros(length, dtype=np.float32)
    for offset, wave in parts:
        end = min(length, offset + len(wave))
        mix[offset:end] += wave[:end-offset] * 0.90
    sf.write(OUT / "dialogue.wav", np.clip(mix,-0.99,0.99), RATE)

    # Original music box loop. Low volume in the final mix so voices remain clear.
    music = np.zeros(length,dtype=np.float32)
    melody = [392,440,523.25,659.25,587.33,523.25,440,392,
              349.23,392,440,523.25,440,392,329.63,349.23]
    step_seconds=0.42
    for ix in range(math.ceil(duration / step_seconds)):
        onset = int(ix * step_seconds * RATE)
        n = min(int(RATE*0.45), length-onset)
        if n<=0: break
        t = np.arange(n,dtype=np.float32)/RATE
        env = (1-np.exp(-42*t))*np.exp(-7*t)
        hz=melody[ix%len(melody)]
        music[onset:onset+n] += 0.17*env*(np.sin(2*np.pi*hz*t)+0.30*np.sin(4*np.pi*hz*t))
    for at in np.arange(0,duration,1.68):
        offset=int(at*RATE)
        n=min(int(1.5*RATE),length-offset)
        if n<=0: break
        t=np.arange(n,dtype=np.float32)/RATE
        for hz in ([196,246.94,293.66] if int(at / 1.68)%2 else [174.61,220,261.63]):
            music[offset:offset+n] += 0.015*np.sin(2*np.pi*hz*t)*np.minimum(1,t*3)*np.exp(-0.38*t)
    sf.write(OUT / "music.wav", np.clip(music,-0.95,0.95), RATE)
    meta={"duration":duration,"fps":12,"lines":entries, "storm_at":entries[3]["start"]+1.5}
    (OUT / "timeline.json").write_text(json.dumps(meta,indent=2),encoding="utf8")
    def srt_time(t):
        ms = round(t * 1000)
        hh, ms = divmod(ms, 3600000)
        mm, ms = divmod(ms, 60000)
        ss, ms = divmod(ms, 1000)
        return f"{hh:02}:{mm:02}:{ss:02},{ms:03}"
    srt = []
    for k, item in enumerate(entries, 1):
        actor = "PIP" if item["speaker"] == "pip" else "PUFF"
        srt.extend([str(k), srt_time(item["start"]) + " --> " + srt_time(item["start"] + item["duration"]), actor + ": " + item["text"], ""])
    (OUT / "captions.srt").write_text("\n".join(srt) + "\n", encoding="utf8")
    print("Total seconds",duration,flush=True)

if __name__=="__main__":
    main()
