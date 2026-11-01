import React from "react";
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";

export type Speaker = "sun" | "flower" | "cloud";
export type StoryLine = {speaker: Speaker; text: string; start: number; duration: number};
export type KidsGardenProps = {dialogue: StoryLine[]; duration: number};

const FONT = "'DejaVu Sans', 'Noto Sans', Arial, sans-serif";
const GOLD = "#FFB940";
const PINK = "#FF78A6";

export const KidsGarden: React.FC<KidsGardenProps> = ({dialogue = [], duration = 60}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;
  const current = dialogue.find((line) => time >= line.start && time < line.start + line.duration);
  const isSpeaking = (name: Speaker) => current?.speaker === name;
  const mouth = (name: Speaker) => isSpeaking(name) && Math.sin(time * 21) > -0.25;
  const blinking = Math.sin(time * 2.3) > 0.994;
  const rainStart = dialogue[4]?.start ?? 1000;
  const rainEnd = (dialogue[5]?.start ?? 1000) + 0.3;
  const raining = time >= rainStart && time <= rainEnd;
  const blooming = time >= (dialogue[5]?.start ?? 1000);
  const countStart = dialogue[7]?.start ?? 1000;
  const counting = time >= countStart && time <= countStart + 3.7;
  const activeCount = Math.min(3, Math.max(1, Math.floor((time - countStart) / 1.2) + 1));
  const intro = time < 1.9;
  const ending = time > duration - 2.3;
  const rise = spring({frame: Math.max(0, frame - 3), fps, config: {damping: 16, stiffness: 75}});
  const sunBob = Math.sin(time * 1.4) * 7;
  const cloudBob = Math.sin(time * 1.6 + 1) * 10;
  const flowerBob = Math.sin(time * 2.3) * 5;
  const fade = interpolate(frame, [0, 16, duration * fps - 18, duration * fps], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{backgroundColor:"#B5ECFF", opacity:fade, fontFamily:FONT, overflow:"hidden"}}>
      <svg viewBox="0 0 1280 720" width="100%" height="100%" style={{position:"absolute",inset:0}}>
        <defs>
          <linearGradient id="kid-sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#91DCFF"/>
            <stop offset="0.69" stopColor="#E5F9FF"/>
            <stop offset="1" stopColor="#FFF7DB"/>
          </linearGradient>
          <linearGradient id="kid-meadow" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#A4E77E"/>
            <stop offset="1" stopColor="#55C874"/>
          </linearGradient>
          <filter id="kid-shadow" x="-40%" y="-50%" width="180%" height="200%">
            <feDropShadow dx="0" dy="8" stdDeviation="9" floodColor="#34858D" floodOpacity="0.18"/>
          </filter>
        </defs>
        <rect width="1280" height="720" fill="url(#kid-sky)"/>
        <path d="M0 465 Q165 344 340 463 T720 467 T1280 445 V720 H0Z" fill="#B6EEA7"/>
        <path d="M0 520 Q215 430 390 520 T800 498 T1280 510 V720 H0Z" fill="url(#kid-meadow)"/>
        <path d="M0 599 Q220 530 480 590 T970 582 T1280 594 V720 H0Z" fill="#6ACF7D" opacity=".52"/>

        {Array.from({length: 24}, (_,i) => {
          const x = 35 + i * 57 + (i % 3) * 11;
          const y = 525 + (i % 5) * 24;
          return <g key={"grass"+i} opacity=".50" transform={`translate(${x},${y})`}>
            <path d="M0 0 l-6 -14 M0 0 l5 -12 M0 0 v-18" fill="none" stroke="#248C59" strokeWidth="3" strokeLinecap="round"/>
          </g>;
        })}

        {/* Friendly, talking sun */}
        <g transform={`translate(1040,${163 + sunBob})`} filter="url(#kid-shadow)">
          {Array.from({length:12}, (_,i) => {
            const angle = (i * Math.PI * 2 / 12) + time * 0.04;
            return <line key={i} x1={Math.cos(angle)*90} y1={Math.sin(angle)*90}
              x2={Math.cos(angle)*116} y2={Math.sin(angle)*116}
              stroke="#FFD358" strokeWidth="13" strokeLinecap="round"/>;
          })}
          <circle r="83" fill="#FFD861" stroke="#FFC546" strokeWidth="7"/>
          <ellipse cx="-42" cy="21" rx="17" ry="10" fill="#FFAF78" opacity=".60"/>
          <ellipse cx="42" cy="21" rx="17" ry="10" fill="#FFAF78" opacity=".60"/>
          <ellipse cx="-29" cy="-13" rx="6" ry={blinking?1.5:9} fill="#714D4F"/>
          <ellipse cx="29" cy="-13" rx="6" ry={blinking?1.5:9} fill="#714D4F"/>
          {mouth("sun") ? <ellipse cy="25" rx="17" ry="18" fill="#A95054"/> :
            <path d="M-19 18 Q0 44 19 18" fill="none" stroke="#A95054" strokeWidth="6" strokeLinecap="round"/>}
        </g>
        <g transform={`translate(1039,${301+sunBob})`}>
          <rect x="-80" y="-22" width="160" height="40" rx="20" fill="#FFF9DB" stroke="#FFE4A9" strokeWidth="2"/>
          <text textAnchor="middle" y="7" fontSize="24" fontWeight="800" fill="#A56A27">Ο ΗΛΙΟΣ</text>
        </g>

        {/* Little cloud Loulis */}
        <g transform={`translate(385,${173+cloudBob})`} filter="url(#kid-shadow)">
          <path d="M-151 45 Q-175 -4 -127 -33 Q-108 -50 -80 -43 Q-69 -111 -2 -104 Q55 -104 71 -65 Q116 -86 146 -43 Q200 -11 163 48 Q153 70 115 70 H-116 Q-150 71 -151 45Z"
            fill="#FFFFFF" stroke="#D6EDFF" strokeWidth="8"/>
          <ellipse cx="-51" cy="6" rx="8" ry={blinking?1.5:12} fill="#475B7B"/>
          <ellipse cx="50" cy="6" rx="8" ry={blinking?1.5:12} fill="#475B7B"/>
          <ellipse cx="-95" cy="31" rx="19" ry="11" fill="#FFC0D0" opacity=".70"/>
          <ellipse cx="95" cy="31" rx="19" ry="11" fill="#FFC0D0" opacity=".70"/>
          {mouth("cloud") ? <ellipse cy="34" rx="19" ry="17" fill="#7B7C9A"/> :
            <path d="M-24 28 Q0 52 24 28" fill="none" stroke="#7B7C9A" strokeWidth="7" strokeLinecap="round"/>}
        </g>
        <g transform={`translate(386,${298+cloudBob})`}>
          <rect x="-103" y="-22" width="206" height="42" rx="21" fill="#FDFDFF" stroke="#B1DDFF" strokeWidth="2"/>
          <text y="8" textAnchor="middle" fontSize="23" fontWeight="800" fill="#4A7DAA">Ο ΛΟΥΛΗΣ</text>
        </g>

        {/* Flower Mina: petals, eyes, smiling animated mouth */}
        <g transform={`translate(644,${463+flowerBob})`}>
          <path d="M0 -10 Q-13 72 2 139" fill="none" stroke="#2E9F61" strokeWidth="18" strokeLinecap="round"/>
          <path d="M0 62 Q-85 10 -92 63 Q-57 108 0 80Z" fill="#48B86A" stroke="#2B9E5E" strokeWidth="4"/>
          <path d="M0 98 Q85 45 93 91 Q65 132 2 119Z" fill="#59C67B" stroke="#2B9E5E" strokeWidth="4"/>
          <g transform={`translate(0,-75) scale(${blooming?1.13:1}) rotate(${Math.sin(time*1.6)*4})`}>
            {Array.from({length:8},(_,i)=><ellipse key={i} cx="0" cy="-66" rx="37" ry="58"
              fill={i%2===0?"#FFA0C2":"#FF7CAB"} stroke="#F46D9D" strokeWidth="3"
              transform={`rotate(${i*45})`}/>)}
            <circle r="64" fill="#FFE391" stroke="#FFC957" strokeWidth="6"/>
            <ellipse cx="-23" cy="-12" rx="7" ry={blinking?1.5:10} fill="#76526B"/>
            <ellipse cx="23" cy="-12" rx="7" ry={blinking?1.5:10} fill="#76526B"/>
            <ellipse cx="-43" cy="13" rx="12" ry="8" fill="#FFA2B4" opacity=".75"/>
            <ellipse cx="43" cy="13" rx="12" ry="8" fill="#FFA2B4" opacity=".75"/>
            {mouth("flower") ? <ellipse cy="23" rx="18" ry="17" fill="#A35370"/> :
              <path d="M-20 16 Q0 38 20 16" fill="none" stroke="#A35370" strokeWidth="6" strokeLinecap="round"/>}
          </g>
        </g>
        <g transform={`translate(649,${588+flowerBob})`}>
          <rect x="-99" y="-22" width="198" height="42" rx="21" fill="#FFF2F7" stroke="#FFC5DA" strokeWidth="2"/>
          <text y="8" textAnchor="middle" fontSize="23" fontWeight="800" fill="#D14F7E">Η ΜΙΝΑ</text>
        </g>

        {/* Animated rain and gentle floating sparkle shapes */}
        {raining && Array.from({length:12},(_,i)=>{
          const progress=((time-rainStart)*105 + i*43)%270;
          const x=380 + i*17 + Math.sin(i*3)*25 + progress*.35;
          const y=278 + progress;
          return <g key={i} transform={`translate(${x},${y})`} opacity={0.48 + 0.4*Math.sin(i+1)**2}>
            <path d="M0 -13 Q11 5 0 13 Q-11 5 0 -13Z" fill="#68C9F7" stroke="#35ACDE" strokeWidth="2"/>
          </g>;
        })}
        {Array.from({length:8},(_,i)=>{
          const x=90 + (i*163)%1120;
          const y=90 + (i*67)%390 + Math.sin(time*1.4+i)*9;
          const sz=4+(i%3)*2;
          return <path key={"sparkle"+i} d={`M${x} ${y-sz*2} L${x+sz} ${y} L${x} ${y+sz*2} L${x-sz} ${y}Z`}
            fill={i%2 ? "#FFF8BA":"#FFFFFF"} opacity=".68"/>;
        })}

        {counting && <g transform="translate(829,367)">
          <circle r="58" fill="#FFFFFF" opacity=".91" stroke="#FFD66D" strokeWidth="6"/>
          <text fontSize="76" fontWeight="900" textAnchor="middle" y="28" fill="#F08B52">{activeCount}</text>
        </g>}
      </svg>

      {intro && <div style={{
        position:"absolute",left:0,right:0,top:20,textAlign:"center",
        transform:`scale(${0.95 + rise*.05})`,color:"#256976",fontSize:46,fontWeight:900,
        textShadow:"0 4px 0 #FFFFFF"
      }}>Η Μίνα και το Συννεφάκι!</div>}

      {current && <div style={{
        position:"absolute",bottom:24,left:110,right:110,minHeight:92,
        background:"rgba(255,255,255,0.95)",border:"6px solid #FFF2B6",
        borderRadius:32,boxShadow:"0 9px 24px rgba(27,106,104,0.18)",
        display:"flex",alignItems:"center",justifyContent:"center",padding:"15px 32px",
        textAlign:"center",fontSize:31,fontWeight:800,lineHeight:1.23,
        color:current.speaker==="flower"?"#B74770":current.speaker==="cloud"?"#4277A6":"#996117",
      }}>{current.text}</div>}

      {ending && <div style={{
        position:"absolute",left:0,right:0,top:27,textAlign:"center",
        fontSize:52,fontWeight:900,color:"#E57C6E",textShadow:"2px 3px 0 #FFFFFF",
      }}>Η καλοσύνη ανθίζει! ♥</div>}
    </AbsoluteFill>
  );
};
