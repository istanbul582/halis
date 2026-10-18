#!/usr/bin/env python3
"""Rebuild the complete 164.2-second original procedural score and narration mix."""
import argparse
from pathlib import Path
import subprocess
import sys
from audio_common import validate_voice


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice', type=Path, required=True,
                        help='Private, complete normalized narration-master.wav; exact SHA-256 is checked.')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent / 'build')
    args = parser.parse_args()
    try:
        validate_voice(args.voice)
    except ValueError as exc:
        parser.error(str(exc))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    folder = Path(__file__).resolve().parent
    for script in ('make_sound_design.py', 'mix_audio.py'):
        subprocess.run([sys.executable, str(folder / script), '--voice', str(args.voice.resolve()),
                        '--output-dir', str(args.output_dir.resolve())], check=True)
    print('Complete audio ready: ' + str(args.output_dir / 'finalmix.wav'))


if __name__ == '__main__':
    main()
