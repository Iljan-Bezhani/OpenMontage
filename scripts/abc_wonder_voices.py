#!/usr/bin/env python3
"""ABC Wonder Garden - original English preschool dialogue + music, zero paid APIs.

Kokoro open-weight TTS drives two recurring characters. This demo teaches A, B
and C with simple repetition. All instrumental notes and foley are original.
"""
import json
import math
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline

RATE=24000
OUT=Path("abc-build")
OUT.mkdir(exist_ok=True)

SCRIPT=[
 ("lulu","Hello, little explorers! I'm Lulu the bunny.", "intro"),
 ("milo","And I'm Milo the bear! Welcome to our A B C wonder garden!", "intro"),
 ("lulu","Are you ready to learn with us? Wiggle your ears and say, yay!", "intro"),
 ("milo","Here comes the letter A! A!", "apple"),
 ("lulu","A is for apple. Apple! A, a, apple!", "apple"),
 ("milo","Look at this big, shiny, red apple. What color is it?", "apple"),
 ("lulu","Red! That's right! Can you say apple? Apple!", "apple"),
 ("milo","Here comes the letter B! B!", "balloon"),
 ("lulu","B is for balloon. B, b, balloon!", "balloon"),
 ("milo","Our balloon is floating up, up, up!", "balloon"),
 ("lulu","Bye-bye, little balloon! Let's wave together!", "balloon"),
 ("milo","Here comes the letter C! C!", "cat"),
 ("lulu","C is for cat! C, c, cat! Meow!", "cat"),
 ("milo","Look at the kitty. It has two tiny ears and a swishy tail!", "cat"),
 ("lulu","Can you meow like a cat? Meow! You're amazing!", "cat"),
 ("milo","Let's remember our letters. A is for apple!", "review"),
 ("lulu","B is for balloon!", "review"),
 ("milo","C is for cat!", "review"),
 ("lulu","Now say them with us! A! B! C!", "review"),
 ("milo","Hooray! You did it! Give yourself a big clap!", "outro"),
 ("lulu","Keep shining, little stars! See you next time!", "outro"),
]

def timecode(seconds):
    ms=round(seconds*1000)
    h,ms=divmod(ms,3600000)
    m,ms=divmod(ms,60000)
    s,ms=divmod(ms,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def main():
    engine=KPipeline(lang_code="a",device="cpu")
    timeline=[]
    voices=[]
    cursor=2.0
    for i,(speaker,line,section) in enumerate(SCRIPT):
        voice="af_heart" if speaker=="lulu" else "am_michael"
        generated=[np.asarray(audio,dtype=np.float32) for _,_,audio in engine(line,voice=voice,speed=0.98)]
        if not generated:
            raise RuntimeError("Empty speech "+str(i))
        sound=np.concatenate(generated)
        start=round(cursor,3)
        dur=len(sound)/RATE
        voices.append((round(start*RATE), sound))
        timeline.append({"speaker":speaker,"text":line,"section":section,
                         "start":start,"duration":round(dur,3)})
        cursor+=dur+(1.3 if i in (2,6,10,14,18) else 0.45)
        print(f"{i+1:02} {section:8} {speaker:5} {start:.2f}: {line}",flush=True)

    duration=math.ceil((cursor+2.2)*12)/12
    n=int(duration*RATE)
    dialogue=np.zeros(n,dtype=np.float32)
    for off,sound in voices:
        bound=min(n,off+len(sound))
        dialogue[off:bound]+=0.88*sound[:bound-off]
    sf.write(OUT/"dialogue.wav",np.clip(dialogue,-1,1),RATE)

    # Original bouncy nursery instrumental, not a copy of the ABC Song tune.
    music=np.zeros(n,dtype=np.float32)
    tempo=0.45
    tune=[392.00,523.25,587.33,523.25,440.0,392.0,329.63,392.0,
          349.23,440.00,523.25,440.0,392.0,349.23,329.63,392.0]
    for step in range(math.ceil(duration/tempo)):
        at=round(step*tempo*RATE)
        lim=min(round(RATE*.42),n-at)
        if lim<=0: break
        t=np.arange(lim,dtype=np.float32)/RATE
        hz=tune[step%len(tune)]
        env=(1-np.exp(-35*t))*np.exp(-8*t)
        signal=(np.sin(2*np.pi*hz*t)+0.23*np.sin(4*np.pi*hz*t))
        music[at:at+lim]+=0.23*env*signal
        # gentle percussive click on each beat
        ki=min(round(RATE*.07),n-at)
        ti=np.arange(ki,dtype=np.float32)/RATE
        music[at:at+ki]+=0.065*np.exp(-60*ti)*np.sin(2*np.pi*(870+100*ti)*ti)
    roots=[261.63,196.0,220.0,174.61]
    for k,at_sec in enumerate(np.arange(0,duration,tempo*4)):
        at=int(at_sec*RATE)
        lim=min(round(RATE*1.65),n-at)
        if lim<=0: break
        t=np.arange(lim,dtype=np.float32)/RATE
        root=roots[k%len(roots)]
        for mult in (1,1.26,1.50):
            music[at:at+lim]+=0.025*np.sin(2*np.pi*root*mult*t)*np.minimum(1,t*4)*np.exp(-0.7*t)
        music[at:at+lim]+=0.060*np.sin(2*np.pi*(root/2)*t)*np.exp(-3*t)
    fade=np.minimum(1,np.arange(n)/RATE/.5)*np.minimum(1,(duration-np.arange(n)/RATE)/1.1)
    sf.write(OUT/"music.wav",np.clip(music*fade,-0.95,0.95),RATE)

    srt=[]
    for k,l in enumerate(timeline,1):
        # short subtitles; no private or hidden text
        srt.extend([str(k),timecode(l["start"])+" --> "+timecode(l["start"]+l["duration"]),
                    l["text"],""])
    (OUT/"captions.srt").write_text("\n".join(srt)+"\n",encoding="utf-8")
    (OUT/"timeline.json").write_text(
        json.dumps({"fps":12,"duration":duration,"lines":timeline},indent=2),encoding="utf-8")
    print(f"OUTPUT audio ready, duration {duration:.1f}s",flush=True)

if __name__=="__main__":
    main()
