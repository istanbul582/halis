#!/usr/bin/env python3
"""Check the actual delivered master, including its complete narration report."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
from fractions import Fraction


def atoms(path):
    found = {}
    with path.open('rb') as f:
        end = path.stat().st_size
        while f.tell() + 8 <= end:
            pos = f.tell()
            size, name = struct.unpack('>I4s', f.read(8))
            if size == 1:
                size = struct.unpack('>Q', f.read(8))[0]
            elif size == 0:
                size = end - pos
            if size < 8:
                raise ValueError('Invalid MP4 atom size')
            found[name.decode('ascii', errors='replace')] = pos
            f.seek(pos + size)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('film', type=Path)
    ap.add_argument('--narration-report', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(a.film)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    au = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    voice = json.loads(a.narration_report.read_text())
    mp4_atoms = atoms(a.film)
    decode = subprocess.run([
        'ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-err_detect', 'explode',
        '-threads', '2', '-i', str(a.film), '-map', '0:v:0', '-map', '0:a:0',
        '-f', 'null', '-'], capture_output=True, text=True)
    loud = subprocess.run([
        'ffmpeg', '-nostdin', '-hide_banner', '-i', str(a.film), '-map', '0:a:0',
        '-vn', '-af', 'loudnorm=I=-16:TP=-1:LRA=10:print_format=json',
        '-f', 'null', '-'], capture_output=True, text=True, check=True)
    measurements = json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}', loud.stderr)[-1])
    checks = {
        'portrait_1080x1920': (v['width'], v['height']) == (1080, 1920),
        'exact_4926_frames': int(v['nb_frames']) == 4926,
        'constant_30fps': Fraction(v['avg_frame_rate']) == 30 and Fraction(v['r_frame_rate']) == 30,
        'h264_yuv420p': v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p',
        'limited_bt709': all(v.get(k) == val for k, val in {
            'color_range': 'tv', 'color_space': 'bt709',
            'color_primaries': 'bt709', 'color_transfer': 'bt709'}.items()),
        'full_164_2_seconds': abs(float(probe['format']['duration']) - 164.2) < .06,
        'aac_stereo_48khz': au['codec_name'] == 'aac' and au['channels'] == 2 and int(au['sample_rate']) == 48000,
        'faststart': mp4_atoms.get('moov', float('inf')) < mp4_atoms.get('mdat', -1),
        'whole_file_decodes': decode.returncode == 0,
        'entire_original_narration_matches': voice.get('passed') is True and voice.get('failed_windows') == 0,
        'original_closing_words_match': bool(voice.get('windows')) and voice['windows'][-1]['matched'] is True and voice['windows'][-1]['voice_start'] > 153.6,
        'integrated_loudness_near_minus16': abs(float(measurements['input_i']) + 16) < 1,
        'true_peak_below_minus1_dbtp': float(measurements['input_tp']) <= -1,
    }
    report = {
        'file': a.film.name, 'bytes': a.film.stat().st_size,
        'sha256': hashlib.sha256(a.film.read_bytes()).hexdigest(),
        'checks': checks, 'passed': all(checks.values()),
        'video': v, 'audio': au, 'duration_seconds': float(probe['format']['duration']),
        'input_audio_measurements': measurements, 'mp4_atom_positions': mp4_atoms,
        'decoder_stderr': decode.stderr, 'narration_report': a.narration_report.name,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'checks': checks, 'sha256': report['sha256'], 'bytes': report['bytes']}, ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
