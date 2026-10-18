"""Original, sample-free 100 BPM score and transitions for the 99s film."""
from pathlib import Path
import json
import subprocess
import numpy as np
from scipy import signal

ROOT = Path(__file__).resolve().parent
SR, LENGTH, BPM = 48000, 99.0, 100
RNG = np.random.default_rng(20261018)
N = round(SR * LENGTH)
music = np.zeros((N, 2), dtype=np.float32)
effects = np.zeros_like(music)


def add(dst, waveform, when, gain=1, pan=0):
    start = round(when * SR)
    if start >= len(dst):
        return
    wave = np.asarray(waveform, dtype=np.float32)
    if start < 0:
        wave, start = wave[-start:], 0
    wave = wave[:len(dst) - start]
    # Equal-power pan, with restrained stereo placement.
    p = np.clip(pan, -1, 1)
    gains = np.array([np.cos((p + 1) * np.pi / 4), np.sin((p + 1) * np.pi / 4)])
    dst[start:start + len(wave)] += wave[:, None] * (gain * gains)[None, :]


def pluck(hz, duration=1.25, bass=False):
    t = np.arange(round(SR * duration)) / SR
    attack = 1 - np.exp(-t / (0.025 if bass else 0.009))
    env = attack * np.exp(-t / (0.52 if bass else 0.31))
    wave = np.sin(2 * np.pi * hz * t) + (0.15 if bass else 0.30) * np.sin(2 * np.pi * hz * 2 * t)
    wave += 0.07 * np.sin(2 * np.pi * hz * 3 * t)
    return wave * env


def wood_tap():
    t = np.arange(round(SR * 0.065)) / SR
    return (0.65 * np.sin(2 * np.pi * 720 * t) + 0.25 * RNG.normal(0, 1, len(t))) * np.exp(-t / .012) * np.minimum(t / .002, 1)


def airy_reverse():
    duration = .34
    t = np.arange(round(SR * duration)) / SR
    noise = RNG.normal(0, 1, len(t))
    filtered = signal.sosfilt(signal.butter(2, [850, 4800], btype='bandpass', fs=SR, output='sos'), noise)
    env = np.where(t < .25, (t / .25) ** 2.1, np.exp(-(t - .25) / .028))
    return filtered * env


def bell(hz, duration=.6):
    t = np.arange(round(SR * duration)) / SR
    return (np.sin(2*np.pi*hz*t) + .18*np.sin(2*np.pi*hz*2.002*t)) * (1-np.exp(-t/.003))*np.exp(-t/.15)


# A simple original C add9 / F major7 / G6 / C major pattern, sixteenth-note
# fills deliberately omitted. No suspense drones, film hits or external loops.
beat = 60 / BPM
chords = [([261.626, 329.628, 440.0], 65.406),
          ([261.626, 349.228, 440.0], 87.307),
          ([293.665, 391.995, 493.883], 97.999),
          ([261.626, 329.628, 391.995], 65.406)]
for bar in range(int(LENGTH / (beat * 4)) + 1):
    onset = bar * beat * 4
    notes, bass_hz = chords[(bar // 2) % len(chords)]
    add(music, pluck(bass_hz, 1.6, bass=True), onset, .038, -.10)
    for offset, note, pan in [(1.5, notes[0], -.25), (3, notes[1], .22)]:
        add(music, pluck(note), onset + offset * beat, .023, pan)
        add(music, pluck(note), onset + offset * beat + .115, .004, -pan)
    if bar % 2 == 1:
        add(music, pluck(notes[2]), onset + 3.5 * beat, .018, .16)
    if bar % 4 in (1, 3):
        add(music, wood_tap(), onset + 2 * beat, .008, -.2)

events = []
for i, cue in enumerate([14.855, 21.010, 25.775, 31.810, 45.995, 59.720, 70.325, 82.450]):
    add(effects, airy_reverse(), cue - .25, .030, (-.28 if i % 2 else .28))
    add(effects, wood_tap(), cue, .024, 0)
    events.append({'time': cue, 'type': 'short airy reverse + restrained wood accent', 'purpose': 'meaningful section transition'})
for cue in [.13, 4.77]:
    add(effects, wood_tap(), cue, .027, -.08)
    events.append({'time': cue, 'type': 'quiet original wood accent', 'purpose': 'opening quote and role reveal'})
for cue, hz in [(90.0, 523.251), (96.0, 659.255), (96.15, 783.991)]:
    add(effects, bell(hz), cue, .026, .12 if cue > 90 else -.12)
    events.append({'time': cue, 'type': 'short original harmonic accent', 'purpose': 'source card / follow animation'})

# Decode the user's own narrator; no original brand/reference audio is read.
raw = subprocess.run(['ffmpeg','-v','error','-i',str(ROOT/'GUMA_v5_full_90s.wav'),'-ar',str(SR),'-ac','1','-f','f32le','-'], check=True, stdout=subprocess.PIPE).stdout
voice_mono = np.frombuffer(raw, dtype='<f4')
voice = np.zeros((N, 2), dtype=np.float32)
voice[:len(voice_mono)] = voice_mono[:, None]

# RMS speech detector with a gentle release; music remains quiet between words.
energy = np.pad(voice_mono**2, (0, N-len(voice_mono))).astype(np.float64)
cumulative = np.concatenate([[0.0], np.cumsum(energy)])
power = (cumulative[1:] - cumulative[np.maximum(np.arange(1, N+1)-2400, 0)]) / 2400
speech = np.clip(np.sqrt(np.maximum(power, 0)) / .035, 0, 1)
speech = signal.lfilter([1-np.exp(-1/(SR*.14))], [1, -np.exp(-1/(SR*.14))], speech)
duck = .32 + .68 * (1 - speech)
music *= duck[:, None]
# All generated layers fade gently in/out; voice level is preserved before the
# measured final mastering pass.
fade_in = np.minimum(np.arange(N) / (SR * .35), 1)
fade_out = np.minimum((N - 1 - np.arange(N)) / (SR * 1.2), 1)
music *= (fade_in * fade_out)[:, None]
effects *= fade_out[:, None]
# A measured first pass was too faint (-46 LUFS for the sparse layers).
# Bring the generated layers up 13.06 dB before the final mix/master pass.
music *= 4.5
effects *= 4.5
sfx = music + effects
premix = voice + sfx


def write(name, data):
    path = ROOT / name
    subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-c:a','pcm_s24le',str(path)], check=True, input=data.astype('<f4').tobytes())
    return str(path)


write('sfx_only.wav', sfx)
write('score_only.wav', music)
write('transition_effects_only.wav', effects)
write('mixed_audio_premaster.wav', premix)
meta = {
    'duration': LENGTH, 'sample_rate': SR, 'channels': 2, 'bpm': BPM,
    'creation': 'Original procedural NumPy/SciPy oscillators, seeded noise and filtering; no external recordings, samples or reference audio.',
    'narrator': 'User supplied Ece narration, edited in GUMA_v5_full_90s.wav; only the first 90 seconds contain speech.',
    'rights': 'Generated instrumental/effects layers are original task outputs. User supplied narration retains its existing rights and is not covered by this statement.',
    'ducking': 'RMS-driven music gain 0.32–1.0, smoothed at 140ms; music fades at film tail.',
    'layer_gain_after_first_measurement': '4.5x (+13.06 dB); first sparse bed measured too faint at -46 LUFS before final mastering.',
    'events': events,
    'sample_peaks_dbfs': {name: round(20*np.log10(max(float(np.max(np.abs(data))),1e-10)),3) for name,data in [('score', music),('effects',effects),('sfx_only',sfx),('premaster',premix)]},
}
(ROOT/'sound_design.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2))
print(json.dumps(meta, ensure_ascii=False, indent=2))
