import React from 'react';
import {AbsoluteFill, Audio, staticFile, Sequence, useCurrentFrame, interpolate, spring, useVideoConfig, Easing} from 'remotion';

const C = {bg: '#05070f', ink: '#e8ecf5', dim: '#7b86a3', up: '#ff7a45', down: '#3fa7ff', ok: '#5be3a1', pill: '#ffd166'};
const font = 'Inter, "Helvetica Neue", Arial, sans-serif';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const fade = (f, a, b) => interpolate(f, [a, a + 15, b - 15, b], [0, 1, 1, 0], clamp);

const Stars = () => {
  const f = useCurrentFrame();
  const stars = React.useMemo(() => Array.from({length: 160}, (_, i) => {
    const r = Math.sin(i * 999.13) * 10000; const r2 = Math.sin(i * 77.7) * 10000;
    return {x: (r - Math.floor(r)) * 1920, y: (r2 - Math.floor(r2)) * 1080, s: 1 + (i % 3), v: 0.2 + (i % 5) * 0.15};
  }), []);
  return <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 120%, #14204a 0%, ${C.bg} 60%)`}}>
    {stars.map((s, i) => <div key={i} style={{position: 'absolute', left: (s.x - f * s.v + 1920) % 1920, top: s.y, width: s.s, height: s.s, borderRadius: 9, background: '#fff', opacity: 0.25 + 0.5 * Math.abs(Math.sin(f / 30 + i))}} />)}
  </AbsoluteFill>;
};

const Title = ({children, size = 64, color = C.ink, y = 0, delay = 0, weight = 700}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s = spring({frame: f - delay, fps, config: {damping: 200}});
  return <div style={{fontFamily: font, fontSize: size, fontWeight: weight, color, opacity: s, transform: `translateY(${(1 - s) * 30 + y}px)`, textAlign: 'center', letterSpacing: -1}}>{children}</div>;
};

const Pill = ({x, y, scale = 1, rot = 0}) => (
  <div style={{position: 'absolute', left: x - 60 * scale, top: y - 25 * scale, width: 120 * scale, height: 50 * scale, borderRadius: 50, transform: `rotate(${rot}deg)`, overflow: 'hidden', boxShadow: `0 0 ${40 * scale}px ${C.pill}88`, display: 'flex'}}>
    <div style={{flex: 1, background: C.pill}} /><div style={{flex: 1, background: '#fff'}} />
  </div>
);

// 1. Hook
const Hook = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const drop = spring({frame: f - 40, fps, config: {damping: 12}});
  return <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity: fade(f, 0, 180)}}>
    <div style={{position: 'absolute', top: 230, width: '100%'}}>
      <Title size={36} color={C.dim} weight={500}>International Space Station · 400 km up</Title>
      <Title size={84} delay={12}>An astronaut takes an antibiotic.</Title>
    </div>
    <Pill x={960} y={interpolate(drop, [0, 1], [-100, 700])} scale={1.6} rot={f * 2} />
    <div style={{position: 'absolute', top: 820, width: '100%'}}><Title size={44} color={C.pill} delay={70}>Does it work the same way in space?</Title></div>
  </AbsoluteFill>;
};

// 2. Journey into the body
const Body = ({highlight}) => (
  <svg width="520" height="900" viewBox="0 0 260 450" style={{position: 'absolute', left: 300, top: 90}}>
    <g fill="none" stroke="#3a4870" strokeWidth="3">
      <circle cx="130" cy="45" r="32" />
      <path d="M95 85 Q130 95 165 85 L195 120 L215 240 M95 85 L65 120 L45 240 M95 85 L90 250 L100 440 M165 85 L170 250 L160 440 M90 250 L170 250" />
    </g>
    <ellipse cx="108" cy="165" rx="34" ry="20" fill={C.up} opacity={highlight.liver} />
    <text x="60" y="140" fill={C.ink} fontSize="13" fontFamily={font} opacity={highlight.liver}>liver</text>
    <ellipse cx="105" cy="212" rx="9" ry="16" fill={C.ok} opacity={highlight.kidney} />
    <ellipse cx="155" cy="212" rx="9" ry="16" fill={C.ok} opacity={highlight.kidney} />
    <text x="170" y="216" fill={C.ink} fontSize="13" fontFamily={font} opacity={highlight.kidney}>kidneys</text>
  </svg>
);
const Journey = () => {
  const f = useCurrentFrame();
  const t = interpolate(f, [10, 90, 170], [0, 1, 2], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const px = 300 + 2 * (t < 1 ? interpolate(t, [0, 1], [130, 108]) : interpolate(t, [1, 2], [108, 130]));
  const py = 90 + 2 * (t < 1 ? interpolate(t, [0, 1], [70, 165]) : interpolate(t, [1, 2], [165, 212]));
  const liver = interpolate(f, [70, 100], [0.15, 0.9], clamp), kidney = interpolate(f, [150, 175], [0.15, 0.9], clamp);
  return <AbsoluteFill style={{opacity: fade(f, 0, 180)}}>
    <Body highlight={{liver, kidney}} />
    <div style={{position: 'absolute', left: px - 14, top: py - 14, width: 28, height: 28, borderRadius: 20, background: C.pill, boxShadow: `0 0 40px ${C.pill}`}} />
    <div style={{position: 'absolute', left: 950, top: 300, width: 820, textAlign: 'left'}}>
      <Title size={60}>Two organs decide its fate.</Title>
      <div style={{height: 40}} />
      <div style={{opacity: liver}}><Title size={40} color={C.up} weight={500}>The liver breaks drugs down with CYP enzymes.</Title></div>
      <div style={{height: 20}} />
      <div style={{opacity: kidney}}><Title size={40} color={C.ok} weight={500}>The kidneys pump drugs out into urine.</Title></div>
    </div>
  </AbsoluteFill>;
};

// 3. NASA data streams in
const Data = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const missions = ['OSD-47', 'OSD-48', 'OSD-137', 'OSD-173', 'OSD-242', 'OSD-245', 'OSD-686'];
  const genes = Math.round(interpolate(f, [30, 130], [0, 23394], clamp));
  return <AbsoluteFill style={{opacity: fade(f, 0, 180), justifyContent: 'center', alignItems: 'center'}}>
    {Array.from({length: 40}, (_, i) => <div key={i} style={{position: 'absolute', left: (i * 53) % 1920, top: ((f * (8 + i % 7) + i * 97) % 1300) - 200, fontFamily: 'monospace', fontSize: 18, color: '#2c6cff', opacity: 0.35}}>{(Math.sin(i * f * 0.01 + i) * 2).toFixed(3)}</div>)}
    <Title size={36} color={C.dim} weight={500}>Live data from NASA's Open Science Data Repository</Title>
    <div style={{display: 'flex', gap: 22, margin: '50px 0'}}>
      {missions.map((m, i) => { const s = spring({frame: f - 15 - i * 6, fps, config: {damping: 14}}); return <div key={m} style={{transform: `scale(${s})`, width: 170, height: 110, borderRadius: 18, border: '2px solid #2c6cff', background: '#0b1636', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', fontFamily: font, color: C.ink}}><div style={{fontSize: 16, color: C.dim}}>NASA study</div><div style={{fontSize: 28, fontWeight: 700}}>{m}</div></div>; })}
    </div>
    <Title size={88} delay={20}>{genes.toLocaleString('en-US')} genes</Title>
    <Title size={36} color={C.dim} weight={500} delay={40}>in mouse livers · flight vs ground · 7 missions pooled</Title>
  </AbsoluteFill>;
};

// 4. Liver gauges
const Gauge = ({label, human, pct, color, delay, drugs, note}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s = spring({frame: f - delay, fps, config: {damping: 30}});
  const w = 360 * (1 + (pct / 100) * s);
  const shown = Math.round(pct * s);
  return <div style={{width: 820, fontFamily: font, color: C.ink}}>
    <div style={{fontSize: 30, color: C.dim}}>{label} <span style={{fontSize: 22}}>(human {human})</span></div>
    <div style={{display: 'flex', alignItems: 'center', gap: 30, margin: '20px 0'}}>
      <div style={{position: 'relative', height: 70, width: 520}}>
        <div style={{position: 'absolute', left: 0, top: 0, height: 70, width: 360, borderRadius: 14, border: '2px dashed #3a4870'}} />
        <div style={{position: 'absolute', left: 0, top: 10, height: 50, width: w, borderRadius: 12, background: color, boxShadow: `0 0 40px ${color}88`}} />
      </div>
      <div style={{fontSize: 80, fontWeight: 800, color}}>{shown > 0 ? '+' : ''}{shown}%</div>
    </div>
    <div style={{fontSize: 22, color: C.dim}}>dashed = ground level · same direction in 6 of 7 missions</div>
    <div style={{fontSize: 32, marginTop: 24, opacity: interpolate(f, [delay + 40, delay + 60], [0, 1], clamp)}}>{drugs}</div>
    <div style={{fontSize: 24, color: C.dim, marginTop: 10, opacity: interpolate(f, [delay + 60, delay + 80], [0, 1], clamp)}}>{note}</div>
  </div>;
};
const Liver = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{opacity: fade(f, 0, 300), padding: '110px 120px'}}>
    <Title size={60}>In space, the liver retunes.</Title>
    <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 90}}>
      <Gauge label="Cyp3a11" human="CYP3A4" pct={30} color={C.up} delay={30}
        drugs={<span>Clarithromycin, erythromycin, clindamycin <b style={{color: C.up}}>may clear faster</b></span>}
        note="Lower blood levels would mean a weaker dose." />
      <Gauge label="Cyp1a2" human="CYP1A2" pct={-31} color={C.down} delay={110}
        drugs={<span>Caffeine and melatonin <b style={{color: C.down}}>may linger</b></span>}
        note="Ciprofloxacin also blocks CYP1A2: cipro plus ISS coffee could stack (inferred)." />
    </div>
  </AbsoluteFill>;
};

// 5. Kidney holds steady
const Kidney = () => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const pumps = [['OAT1', 'penicillins'], ['OAT3', 'cephalosporins'], ['OCT2', 'fluoroquinolones'], ['MATE1', 'carbapenems'], ['KIM-1', 'injury marker'], ['NGAL', 'injury marker']];
  return <AbsoluteFill style={{opacity: fade(f, 0, 180), padding: '120px 160px'}}>
    <Title size={60}>The kidneys hold steady.</Title>
    <div style={{display: 'flex', justifyContent: 'center', gap: 40, marginTop: 110}}>
      {pumps.map(([p, d], i) => { const s = spring({frame: f - 10 - i * 7, fps, config: {damping: 15}}); const pulse = 1 + 0.04 * Math.sin(f / 6 + i);
        return <div key={p} style={{textAlign: 'center', fontFamily: font, transform: `translateY(${(1 - s) * 80}px)`, opacity: s}}>
          <div style={{width: 160, height: 160, borderRadius: 90, border: `3px solid ${C.ok}`, background: '#0b2a20', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: 34, fontWeight: 700, color: C.ok, transform: `scale(${pulse})`}}>{p}</div>
          <div style={{color: C.dim, fontSize: 22, marginTop: 18}}>{d}</div></div>; })}
    </div>
    <div style={{marginTop: 90}}><Title size={40} color={C.ok} weight={500} delay={60}>No clear change across 3 missions.</Title></div>
    <Title size={28} color={C.dim} weight={400} delay={80}>Only 3 kidney studies were usable, so this is weak evidence, not proof.</Title>
  </AbsoluteFill>;
};

// 6. End card
const End = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{opacity: interpolate(f, [0, 20], [0, 1], clamp), justifyContent: 'center', alignItems: 'center'}}>
    <Title size={72}>32 antibiotics. 3 may act differently in orbit.</Title>
    <div style={{height: 40}} />
    <Title size={36} color={C.dim} weight={400} delay={25}>Mouse gene activity, not drug levels in people.</Title>
    <Title size={36} color={C.pill} weight={600} delay={40}>A hypothesis worth testing before Mars.</Title>
    <div style={{height: 80}} />
    <Title size={24} color={C.dim} weight={400} delay={60}>Data: NASA OSDR (GeneLab) · Stouffer meta-analysis, genome-wide FDR &lt; 0.05 · space-medicine project</Title>
  </AbsoluteFill>;
};

export const Film = () => (
  <AbsoluteFill style={{background: C.bg}}>
    <Audio src={staticFile('soundtrack.wav')} />
    <Stars />
    <Sequence durationInFrames={180}><Hook /></Sequence>
    <Sequence from={180} durationInFrames={180}><Journey /></Sequence>
    <Sequence from={360} durationInFrames={180}><Data /></Sequence>
    <Sequence from={540} durationInFrames={300}><Liver /></Sequence>
    <Sequence from={840} durationInFrames={180}><Kidney /></Sequence>
    <Sequence from={1020} durationInFrames={210}><End /></Sequence>
  </AbsoluteFill>
);
