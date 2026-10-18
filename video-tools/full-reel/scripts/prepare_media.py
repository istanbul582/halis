#!/usr/bin/env python3
"""Prepare the 11 portrait clips from privately held, user-supplied originals."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.m4v', '.webm'}


def probe(path: Path) -> dict:
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=width,height,avg_frame_rate,nb_frames:format=duration',
         '-of', 'json', str(path)], check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path,
                        help='Recursively searched private directory containing the original ID-prefixed files.')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'assets' / 'clips')
    parser.add_argument('--only', nargs='+', metavar='CLIP',
                        help='Prepare only these clip names; comma-separated names also work.')
    parser.add_argument('--max-seconds', type=float,
                        help='Short validation render only; omit when preparing production clips.')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if not args.source_dir.is_dir():
        parser.error('--source-dir must be an existing directory')
    if args.max_seconds is not None and args.max_seconds <= 0:
        parser.error('--max-seconds must be positive')
    for binary in ('ffmpeg', 'ffprobe'):
        if not shutil.which(binary):
            parser.error(f'{binary} is required on PATH')

    manifest = json.loads((Path(__file__).with_name('media_manifest.json')).read_text())
    wanted = {name for item in (args.only or []) for name in item.split(',') if name}
    if wanted:
        known = {item['name'] for item in manifest}
        unknown = wanted - known
        if unknown:
            parser.error('Unknown --only clip name(s): ' + ', '.join(sorted(unknown)))
        manifest = [item for item in manifest if item['name'] in wanted]

    # Resolve every required input before creating any output. Never download footage.
    candidates = [p for p in args.source_dir.rglob('*')
                  if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS]
    resolved = {}
    failures = []
    for source_id in sorted({item['source_id'] for item in manifest}):
        pattern = re.compile(r'^' + re.escape(source_id) + r'(?:[-_.]|$)')
        matches = [p for p in candidates if pattern.match(p.name)]
        if len(matches) != 1:
            failures.append(f'{source_id}: expected exactly one original, found {len(matches)}')
        else:
            resolved[source_id] = matches[0]
    if failures:
        parser.error('Private source inputs could not be resolved:\n' + '\n'.join(failures))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {'preview_only': args.max_seconds is not None, 'clips': []}
    for item in manifest:
        source = resolved[item['source_id']]
        output = args.output_dir / item['output_filename']
        if output.exists() and not args.overwrite:
            parser.error(f'{output.name} already exists; use --overwrite or a new output directory')
        source_info = probe(source)
        streams = source_info.get('streams', [])
        if not streams:
            parser.error(f'No video stream in source {item["source_id"]}')
        width, height = streams[0]['width'], streams[0]['height']
        crop_w, crop_h, crop_x, crop_y = map(int, item['crop'])
        if min(crop_w, crop_h) <= 0 or min(crop_x, crop_y) < 0 or crop_x + crop_w > width or crop_y + crop_h > height:
            parser.error(f'Crop for {item["name"]} does not fit its original {width}×{height} source')
        duration = float(item['length'])
        if args.max_seconds is not None:
            duration = min(duration, args.max_seconds)
        if float(source_info['format']['duration']) + 0.05 < float(item['source_start']) + duration:
            parser.error(f'Source {item["source_id"]} is shorter than the requested clip')
        temp = output.with_name(output.stem + '.partial.mp4')
        filters = (f'crop={crop_w}:{crop_h}:{crop_x}:{crop_y},'
                   'scale=720:1280:flags=lanczos,fps=30,setsar=1')
        command = [
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
            '-threads', '2', '-filter_threads', '2',
            '-ss', str(item['source_start']), '-i', str(source), '-t', str(duration),
            '-an', '-vf', filters, '-c:v', 'libx264', '-threads', '2',
            '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart', str(temp),
        ]
        try:
            subprocess.run(command, check=True)
            info = probe(temp)
            stream = info['streams'][0]
            if [stream['width'], stream['height']] != [720, 1280] or stream['avg_frame_rate'] != '30/1':
                raise RuntimeError('Unexpected output dimensions or frame rate')
            if abs(float(info['format']['duration']) - duration) > 1 / 30 + 0.001:
                raise RuntimeError('Unexpected output duration')
            temp.replace(output)
        finally:
            temp.unlink(missing_ok=True)
        report['clips'].append({
            'filename': output.name, 'source_id': item['source_id'],
            'source_start': item['source_start'], 'crop': item['crop'],
            'duration_seconds': float(info['format']['duration']),
            'dimensions': [720, 1280], 'fps': 30,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        })
        print(f'Prepared {output.name} ({duration:g}s)', flush=True)
    (args.output_dir / 'prepare-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f'Media preparation failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
