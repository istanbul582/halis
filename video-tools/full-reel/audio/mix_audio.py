#!/usr/bin/env python3
"""Mix the complete private narration with the original procedural score, without edits."""
from pathlib import Path
import argparse
import json
import re
import subprocess
from audio_common import DURATION, VOICE_DURATION, REFERENCE_MIX_SHA256, validate_voice, probe_audio, sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice', required=True, type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent / 'build')
    args = parser.parse_args()
    try:
        voice_info = validate_voice(args.voice)
    except ValueError as exc:
        parser.error(str(exc))
    out = args.output_dir
    sound = out / 'sound-design.wav'
    if not sound.is_file():
        parser.error('sound-design.wav is missing; run make_sound_design.py with the same --voice and --output-dir first')
    sound_info = probe_audio(sound)
    if abs(float(sound_info['format']['duration']) - DURATION) > 0.001:
        parser.error('sound-design.wav must be the complete 164.2-second score')

    def run(command, log_name):
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                text=True, check=True)
        (out / log_name).write_text(result.stderr)
        return result.stderr

    def loudnorm_data(log):
        matches = re.findall(r'\{[\s\S]*?\}', log)
        if not matches:
            raise RuntimeError('FFmpeg loudness measurement did not return JSON')
        return json.loads(matches[-1])

    base = ['ffmpeg', '-hide_banner', '-nostdin', '-threads', '2', '-y']
    before = out / 'mix-before-normalize.wav'
    final = out / 'finalmix.wav'
    # This is the original filter graph. No atrim touches the 7,448,033-sample voice.
    # apad adds silence after its natural end so the source card/CTA can finish.
    run(base + ['-i', str(args.voice), '-i', str(sound), '-filter_complex',
                '[0:a]pan=stereo|c0=c0|c1=c0,apad=whole_dur=164.2[v];'
                '[v][1:a]amix=inputs=2:duration=longest:normalize=0,atrim=duration=164.2[a]',
                '-map', '[a]', '-t', '164.2', '-ar', '48000', '-ac', '2',
                '-c:a', 'pcm_s24le', str(before)], 'mix.log')
    analysis = loudnorm_data(run(base + ['-i', str(before), '-af',
                              'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json',
                              '-f', 'null', '-'], 'mix-loudnorm-analysis.log'))
    loudnorm = (f'loudnorm=I=-16:TP=-1.5:LRA=7:measured_I={analysis["input_i"]}:'
                f'measured_TP={analysis["input_tp"]}:measured_LRA={analysis["input_lra"]}:'
                f'measured_thresh={analysis["input_thresh"]}:offset={analysis["target_offset"]}:'
                'linear=false:print_format=json')
    run(base + ['-i', str(before), '-af', loudnorm, '-t', '164.2', '-ar', '48000',
                '-ac', '2', '-c:a', 'pcm_s24le', str(final)], 'final-mix-loudnorm.log')
    measured = loudnorm_data(run(base + ['-i', str(final), '-af',
                              'loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json',
                              '-f', 'null', '-'], 'final-mix-verification.log'))
    run(['ffmpeg', '-v', 'error', '-nostdin', '-xerror', '-threads', '2', '-i', str(final),
         '-f', 'null', '-'], 'full-decode.log')
    info = probe_audio(final)
    result = {
        'duration_seconds': float(info['format']['duration']),
        'sample_rate': 48000, 'channels': 2, 'codec': 'PCM 24-bit',
        'integrated_loudness_LUFS': float(measured['input_i']),
        'true_peak_dBTP': float(measured['input_tp']),
        'loudness_range_LU': float(measured['input_lra']),
        'voice_input': voice_info, 'voice_duration_seconds': VOICE_DURATION,
        'voice_cut': False, 'voice_reordered': False, 'voice_speed_changed': False,
        'original_audio_source': 'Complete user-supplied ElevenLabs narration only. No source GUMA video audio.',
        'music_source': 'Original deterministic 92 BPM sine/noise synthesis; no sampled music.',
        'foley_source': 'Original deterministic noise/oscillator synthesis; see sfx-events.json.',
        'music_ducking': 'Unchanged narration RMS envelope; approx. 9 dB maximum music duck, mild Foley duck.',
        'sources_card_seconds': [155.2, 161.2], 'follow_animation_seconds': [161.2, 164.2],
        'effect_timing_note': 'The complete original V3 mix is reused unchanged. Its final chime at 162.2s remains inside the V6 CTA.',
        'full_audio_decode': 'passed', 'sha256': sha256(final),
        'reference_mix_sha256': REFERENCE_MIX_SHA256,
    }
    result['matches_reference_mix_bytes'] = result['sha256'] == REFERENCE_MIX_SHA256
    result['ffmpeg_version'] = subprocess.check_output(['ffmpeg', '-version'], text=True).splitlines()[0]
    assert abs(result['duration_seconds'] - DURATION) < 0.001
    assert -16.2 <= result['integrated_loudness_LUFS'] <= -15.8
    assert result['true_peak_dBTP'] <= -1.45
    (out / 'finalmix.metadata.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
