"""Score for the PSIU video: 120 BPM, A minor (Am-F-C-G), every hit on a 0.5 s / 0.125 s grid.

Music and sound effects are one piece: effects use the song's notes (A, C, E, G...) and sit under the
mix. Writes work/music.wav (stereo, 44.1 kHz, 16-bit).
"""
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 22.0
BEAT = 0.5           # 120 BPM
BAR = 2.0
DRUMS_IN, GROOVE_IN, DRUMS_OUT = 3.0, 6.5, 20.0

rng = np.random.default_rng(7)
mix_l = np.zeros(int(SR * DUR))
mix_r = np.zeros(int(SR * DUR))


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def tvec(seconds):
    return np.arange(int(SR * seconds)) / SR


def filt(x, kind, freq, order=2):
    sos = butter(order, freq, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def place(x, start, gain=1.0, pan=0.0):
    """Add mono signal x at `start` seconds; pan -1 (left) .. 1 (right)."""
    i = int(round(start * SR))
    if i >= len(mix_l):
        return
    x = x[: len(mix_l) - i] * gain
    mix_l[i : i + len(x)] += x * np.sqrt((1 - pan) / 2) * np.sqrt(2)
    mix_r[i : i + len(x)] += x * np.sqrt((1 + pan) / 2) * np.sqrt(2)


def pluck(midi, length=0.45, bright=6, decay=7.0):
    t = tvec(length)
    f = hz(midi)
    x = sum(np.sin(2 * np.pi * f * k * t) * (0.6 ** (k - 1)) for k in range(1, bright + 1))
    env = np.exp(-t * decay) * np.minimum(1, t / 0.004)
    return x * env / bright * 2


def saw_voice(midi, length, detune=0.0):
    t = tvec(length)
    f = hz(midi) * (1 + detune)
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))


def noise(length):
    return rng.standard_normal(int(SR * length))


# ---------------------------------------------------------------- harmony
AM, F, C, G = (57, 60, 64), (53, 57, 60), (55, 60, 64), (55, 59, 62)
ROOT = {AM: 45, F: 41, C: 48, G: 43}
progression = [AM, F, C, G] * 3
progression[10] = AM                      # last bar resolves home
bars = int(DUR / BAR)

# pad: detuned saws, soft attack, low-passed; wider in stereo
for b in range(bars):
    chord = progression[b]
    length = BAR + 0.5
    env_t = tvec(length)
    env = np.minimum(1, env_t / 0.35) * np.clip((length - env_t) / 0.5, 0, 1)
    for note in chord:
        left = filt(saw_voice(note, length, -0.003) * env, "low", 1700)
        right = filt(saw_voice(note, length, 0.003) * env, "low", 1700)
        i = int(b * BAR * SR)
        n = min(len(left), len(mix_l) - i)
        gain = 0.035 if b * BAR < DRUMS_IN else 0.03
        mix_l[i : i + n] += left[:n] * gain
        mix_r[i : i + n] += right[:n] * gain

# ---------------------------------------------------------------- drums
kick_env = np.zeros(len(mix_l))


def kick():
    t = tvec(0.42)
    freq = 48 + 80 * np.exp(-t * 28)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    body = np.sin(phase) * np.exp(-t * 8)
    click = filt(noise(0.42), "high", 2000) * np.exp(-t * 180) * 0.15
    return body + click


k = kick()
for n in range(int(DRUMS_IN / BEAT), int(DRUMS_OUT / BEAT)):
    start = n * BEAT
    place(k, start, 0.55)
    i = int(start * SR)
    env = np.exp(-tvec(0.3) * 12)
    kick_env[i : i + len(env)] = np.maximum(kick_env[i : i + len(env)], env[: len(kick_env) - i])

hat = filt(noise(0.06), "high", 7500) * np.exp(-tvec(0.06) * 70)
clap = sum(np.pad(filt(noise(0.2), "band", [1100, 3200]) * np.exp(-tvec(0.2) * 22), (int(d * SR), 0))[: int(0.2 * SR)]
           for d in (0, 0.011, 0.022))
for n in range(int(GROOVE_IN / BEAT), int(DRUMS_OUT / BEAT)):
    start = n * BEAT
    place(hat, start + BEAT / 2, 0.07, pan=0.3)
    if n % 2 == 1:
        place(clap, start, 0.16, pan=-0.1)

# ---------------------------------------------------------------- bass (8ths, from the drop)
for n in range(int(DRUMS_IN / 0.25), int(DRUMS_OUT / 0.25)):
    start = n * 0.25
    root = ROOT[progression[int(start // BAR)]]
    if n % 8 in (3, 7):                   # breathing room
        continue
    t = tvec(0.24)
    f = hz(root)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sign(np.sin(2 * np.pi * f * t))
    x = filt(x, "low", 520) * np.exp(-t * 9) * np.minimum(1, t / 0.005)
    place(x, start, 0.22)

# ---------------------------------------------------------------- pluck line (beats, from the groove)
for n in range(int(GROOVE_IN / BEAT), int(DRUMS_OUT / BEAT)):
    start = n * BEAT
    chord = progression[int(start // BAR)]
    pattern = [chord[0], chord[2], chord[1], chord[2]]
    place(pluck(pattern[n % 4] + 12, 0.4, bright=5, decay=9), start, 0.075, pan=-0.25 if n % 2 else 0.25)

# ---------------------------------------------------------------- sound effects (in key, under the mix)
def blip(midi, gain=0.16, pan=0.0, at=0.0):
    place(pluck(midi, 0.3, bright=3, decay=14), at, gain, pan)


def whoosh(cut, gain=0.05):
    length = 0.35
    t = tvec(length)
    shape = np.sin(np.pi * t / length) ** 2
    place(filt(noise(length), "band", [600, 4500]) * shape, cut - 0.2, gain)


# hook: two messages arrive, then the "read" stamp
blip(81, 0.15, pan=-0.2, at=0.5)          # A5: Ana's question
blip(76, 0.15, pan=0.2, at=1.5)           # E5: your answer, with the key
place(pluck(52, 0.5, bright=2, decay=6), 2.0, 0.14)   # low E: "uh-oh, it's in the history"

# riser into the reveal
length = 1.0
rise = np.zeros(int(SR * length))
steps = 12
for s_ in range(steps):
    lo = 300 * (1.35 ** s_)
    seg = filt(noise(length / steps), "band", [lo, min(lo * 2.2, 15000)])
    seg *= (s_ + 1) / steps
    a = int(s_ * len(rise) / steps)
    rise[a : a + len(seg)] = seg[: len(rise) - a]
place(rise * np.linspace(0, 1, len(rise)) ** 2, 2.0, 0.1)

# impact on the drop + tag pop
t = tvec(0.9)
place(np.sin(2 * np.pi * 45 * t) * np.exp(-t * 4.5), 3.0, 0.35)
place(filt(noise(0.5), "low", 900) * np.exp(-tvec(0.5) * 9), 3.0, 0.12)
for note in (69, 76, 81):                 # A4 E5 A5
    place(pluck(note, 0.5, bright=4, decay=8), 3.5, 0.07)
blip(88, 0.04, at=4.0)
blip(84, 0.04, at=4.5)

for cut in (6.5, 10.5, 14.5, 18.0):
    whoosh(cut)


def click(at):
    place(pluck(88, 0.05, bright=2, decay=80), at, 0.12)
    place(filt(noise(0.02), "high", 3000) * np.exp(-tvec(0.02) * 300), at, 0.06)


def chime(at):
    blip(76, 0.11, pan=-0.15, at=at)
    blip(81, 0.11, pan=0.15, at=at + 0.125)


click(8.0); chime(8.5)                    # Pedir: click, "Link copiado"
for n in range(8):                        # typing ••••, on 16ths
    place(filt(noise(0.03), "band", [2500, 6000]) * np.exp(-tvec(0.03) * 160), 11.0 + n * 0.125, 0.035,
          pan=0.15 if n % 2 else -0.15)
click(12.5)                               # Enviar: click + the shackle snaps shut
for note in (69, 76):
    sq = np.sign(np.sin(2 * np.pi * hz(note) * tvec(0.06))) * np.exp(-tvec(0.06) * 60)
    place(filt(sq, "low", 3000), 12.5 + (0.0 if note == 69 else 0.0625), 0.06)
chime(13.0)
blip(81, 0.13, pan=-0.2, at=15.0)         # the reply link arrives in the chat
click(17.0)                               # eye: the secret appears
for i, note in enumerate((81, 84, 88, 93)):
    place(pluck(note, 0.35, bright=3, decay=12), 17.0 + i * 0.125, 0.06, pan=-0.3 + i * 0.2)
for note in (69, 76, 81):                 # end tag
    place(pluck(note, 0.6, bright=4, decay=6), 19.0, 0.06)
place(pluck(45, 1.8, bright=3, decay=2.2), 20.0, 0.18)   # final low A as the drums drop out

# ---------------------------------------------------------------- mix
duck = 1 - 0.3 * kick_env                 # pad and bass breathe with the kick
mix = np.stack([mix_l, mix_r]) * duck
mix = np.tanh(mix * 1.3) / np.tanh(1.3)   # gentle glue, no hard clipping
fade_in = np.minimum(1, tvec(DUR) / 0.05)
fade_out = np.clip((DUR - tvec(DUR)) / 1.2, 0, 1)
mix *= fade_in * fade_out
mix *= 0.89 / np.max(np.abs(mix))

out = Path(__file__).parent / "music.wav"
wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
print(out, f"{DUR}s", "peak", round(float(np.max(np.abs(mix))), 3))
