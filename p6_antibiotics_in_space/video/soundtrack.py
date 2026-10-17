"""Synthesize the video's soundtrack (41 s, stereo) and mix in the voiceover.

Music is all generated. The voiceover lines are vo/line_N.wav (made by voiceover.py);
the music ducks under them."""
import wave
import numpy as np

SR, DUR = 44100, 41.0
t = np.arange(int(SR * DUR)) / SR
L = np.zeros_like(t); R = np.zeros_like(t)
rng = np.random.default_rng(7)
note = lambda m: 440 * 2 ** ((m - 69) / 12)

def env(start, a, d, n=None):
    n = n or len(t); x = t - start
    return np.where(x < 0, 0, np.where(x < a, x / a, np.exp(-(x - a) / d)))

def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")

# Ambient pad: Am - F - C - G, 9.5 s each, detuned sines
chords = [[45, 57, 60, 64], [41, 53, 57, 60], [48, 55, 60, 64], [43, 55, 59, 62]]
for i, ch in enumerate(chords):
    s, e = i * 10.25, i * 10.25 + 11.25
    w = np.clip((t - s) / 2, 0, 1) * np.clip((e - t) / 2, 0, 1)
    for m in ch:
        f = note(m)
        L += 0.05 * w * np.sin(2 * np.pi * f * t)
        R += 0.05 * w * np.sin(2 * np.pi * f * 1.004 * t + 1)

# Sub heartbeat during data and liver scenes (11 s to 27 s)
for b in np.arange(12.0, 28.0, 0.75):
    x = np.clip(t - b, 0, None)
    k = 0.35 * env(b, 0.005, 0.12) * np.sin(2 * np.pi * (55 + 60 * np.exp(-x * 30)) * x)
    L += k; R += k

# Whooshes into each scene
noise = lowpass(rng.standard_normal(len(t)), 30)
for s in [5.6, 11.6, 17.6, 27.6, 33.6]:
    w = np.exp(-((t - s - 0.4) / 0.35) ** 2)
    L += 0.5 * w * noise; R += 0.5 * w * np.roll(noise, 400)

# Pill landing: a bright ping
for f, g in [(note(84), 0.25), (note(91), 0.12)]:
    p = g * env(2.0, 0.003, 0.6) * np.sin(2 * np.pi * f * t)
    L += p; R += p

# Mission cards pop in (one blip each)
for i in range(7):
    b = 12.0 + (15 + i * 6) / 30
    p = 0.12 * env(b, 0.002, 0.08) * np.sin(2 * np.pi * note(76 + 2 * i) * t)
    L += p; R += p

# Liver gauges: rising sweep for CYP3A up, falling for CYP1A2 down
for start, f0, f1 in [(19.0, 220, 660), (21.7, 660, 180)]:
    x = np.clip(t - start, 0, None)
    f = f0 + (f1 - f0) * np.clip(x / 0.9, 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    g = 0.18 * np.where((t >= start) & (t < start + 1.6), np.minimum(x / 0.05, 1) * np.exp(-x * 1.5), 0)
    L += g * np.sin(ph); R += g * np.sin(ph + 0.3)

# Kidney pumps: soft steady ticks
for b in np.arange(28.4, 33.6, 0.5):
    p = 0.08 * env(b, 0.002, 0.05) * np.sin(2 * np.pi * note(81) * t)
    L += p; R += p

# End: a resolving A-major swell
w = np.clip((t - 34) / 1.5, 0, 1)
for m in [57, 61, 64, 69]:
    L += 0.06 * w * np.sin(2 * np.pi * note(m) * t); R += 0.06 * w * np.sin(2 * np.pi * note(m) * 1.003 * t)

# Voiceover: one line per scene, music ducks to 35% underneath
from pathlib import Path
VO_START = [0.5, 6.4, 12.4, 18.6, 28.6, 34.6]
vo = np.zeros_like(t)
for i, start in enumerate(VO_START, 1):
    f = Path(f"vo/line_{i}.wav")
    if not f.exists():
        continue
    with wave.open(str(f)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2") / 32768
        x = np.interp(np.arange(0, len(x), w.getframerate() / SR), np.arange(len(x)), x)
    a = int(start * SR); vo[a:a + len(x)] += x[:len(vo) - a]
active = lowpass((np.abs(vo) > 0.01).astype(float), int(0.4 * SR))
duck = 1 - 0.65 * np.clip(active * 3, 0, 1)
music_peak = max(np.abs(L).max(), np.abs(R).max())
L = L / music_peak * 0.6 * duck + 0.9 * vo
R = R / music_peak * 0.6 * duck + 0.9 * vo

fade = np.clip(t / 1.0, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
st = np.stack([L, R], 1) * fade[:, None]
st = st / np.abs(st).max() * 0.85
with wave.open("public/soundtrack.wav", "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((st * 32767).astype("<i2").tobytes())
