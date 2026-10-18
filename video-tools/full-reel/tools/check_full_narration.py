#!/usr/bin/env python3
"""Check that the complete supplied voice remains in a mixed film, without cutting.

This is a signal check, not speech recognition or a legal/content review.
It handles background music by comparing aligned short waveform windows.
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import correlate


def audio(path, rate=8000):
    result = subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar',str(rate),'-f','f32le','pipe:1'], capture_output=True, check=True)
    return np.frombuffer(result.stdout, dtype='<f4').astype(np.float64)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--voice', required=True, type=Path)
    p.add_argument('--film', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--expected-offset', type=float, default=0.0)
    p.add_argument('--tolerance', type=float, default=.075)
    a = p.parse_args()
    rate = 8000
    ref, film = audio(a.voice), audio(a.film)
    # Compare every 1.5 second window. Silence windows do not establish voice presence.
    hop, width = int(1.5*rate), int(1.5*rate)
    target, radius = round(a.expected_offset*rate), round(a.tolerance*rate)
    results = []
    starts = list(range(0, len(ref)-width+1, hop))
    # Include the final partial hop so the closing words are independently checked.
    if len(ref) >= width:
        starts = sorted(set(starts + [len(ref)-width]))
    for start in starts:
        x = ref[start:start+width]
        energy = float(np.sqrt(np.mean(x*x)))
        if energy < .002:
            continue
        lo, hi = max(0, target+start-radius), min(len(film), target+start+width+radius)
        y = film[lo:hi]
        if len(y) < len(x):
            results.append({'voice_start':start/rate,'rms':energy,'correlation':0,'matched':False,'reason':'Film ends before the voice window'})
            continue
        xc = x-x.mean()
        scores = correlate(y, xc, mode='valid', method='fft')
        cumulative = np.r_[0,np.cumsum(y*y)]
        energy_y = cumulative[width:]-cumulative[:-width]
        means = np.r_[0,np.cumsum(y)]
        mean_y = means[width:]-means[:-width]
        variance_y = np.maximum(0, energy_y-mean_y**2/width)
        normalized = scores/np.sqrt(np.maximum(1e-20, np.sum(xc*xc)*variance_y))
        best = int(np.argmax(normalized))
        score = float(normalized[best])
        results.append({'voice_start':round(start/rate,3),'rms':round(energy,6),'correlation':round(score,5),'offset_seconds':round((lo+best-start)/rate,6),'matched':bool(score>=.70)})
    failed = [r for r in results if not r['matched']]
    report = {'reference_voice':str(a.voice),'film':str(a.film),'reference_seconds':len(ref)/rate,'film_audio_seconds':len(film)/rate,'method':'8kHz mono waveform correlation; every voiced 1.5 second window plus the final 1.5 seconds; expected global offset and 75ms local tolerance; no speech transcription','reference_fully_fits':len(film)>=target+len(ref)-int(.03*rate),'compared_windows':len(results),'failed_windows':len(failed),'minimum_correlation':min((r['correlation'] for r in results),default=0),'windows':results}
    report['passed'] = bool(report['reference_fully_fits'] and len(results)>=20 and not failed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps({k:v for k,v in report.items() if k!='windows'},ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 2)


if __name__ == '__main__':
    main()
