#!/usr/bin/env python3
"""Frame-accurate visual inventory. This tool never trims or rewrites media."""
from __future__ import annotations
import argparse
import json
import re
import time
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


def font(size: int):
    candidates = [
        str(Path(__file__).resolve().parent.parent / 'film' / 'fonts' / 'Manrope.ttf'),
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def frame_at(container, stream, sec: float):
    container.seek(int(sec / stream.time_base), stream=stream, backward=True)
    last = None
    for frame in container.decode(stream):
        last = frame
        if frame.time is not None and frame.time >= sec:
            break
    if last is None:
        raise ValueError(f'No decodable frame at {sec}')
    return last.to_image().convert('RGB'), float(last.time or 0)


def thumb(image, box=(300, 210)):
    image.thumbnail(box)
    target = Image.new('RGB', box, '#1a2130')
    target.paste(image, ((box[0] - image.width)//2, (box[1]-image.height)//2))
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path.cwd()))
    parser.add_argument('--out', default=str(Path(__file__).parent/'inventory'))
    args = parser.parse_args()
    started = time.monotonic()
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    files = sorted(p for p in Path(args.root).rglob('*.mp4') if re.match(r'^\d{6,}[_-]', p.name))
    overview = Image.new('RGB', (1200, max(1, (len(files)+3)//4)*270), '#101725')
    od = ImageDraw.Draw(overview)
    for i, path in enumerate(files):
        source_id = re.match(r'^(\d+)', path.name).group(1)
        with av.open(str(path)) as container:
            stream = container.streams.video[0]
            stream.thread_type = 'AUTO'
            duration = float(stream.duration*stream.time_base) if stream.duration is not None else container.duration/av.time_base
            samples = []
            sheet = Image.new('RGB', (900, 270), '#101725')
            sd = ImageDraw.Draw(sheet)
            for j, frac in enumerate((.2, .5, .8)):
                image, actual = frame_at(container, stream, max(0, duration*frac))
                tile = thumb(image)
                sheet.paste(tile, (j*300, 30))
                sd.text((j*300+8, 244), f'{actual:.3f} s', font=font(16), fill='#e5e9ef')
                samples.append({'target_seconds': duration*frac, 'decoded_seconds': actual})
                if j == 1:
                    x, y = (i%4)*300, (i//4)*270
                    overview.paste(tile, (x, y+30))
                    od.text((x+8, y+8), source_id, font=font(17), fill='#ffd179')
                    od.text((x+8, y+243), f'{duration:.2f}s | {stream.width}x{stream.height}', font=font(14), fill='#e5e9ef')
            sd.text((8, 6), f'{source_id} | {duration:.3f}s | {stream.width}x{stream.height}', font=font(16), fill='#ffd179')
            sheet.save(output/f'{source_id}.jpg', quality=88)
            rows.append({
                'source_id': source_id, 'path': str(path),
                'duration_seconds': duration, 'fps': str(stream.average_rate),
                'width': stream.width, 'height': stream.height,
                'audio_tracks': len(container.streams.audio),
                'contact_sheet': f'{source_id}.jpg', 'samples': samples,
                'source_url': f'https://www.pexels.com/video/{source_id}/',
                'source_status': 'Pexels according to user; original page/license not independently verified',
            })
    overview.save(output/'overview.jpg', quality=90)
    report = {'tool': f'PyAV {av.__version__}', 'action': 'Read metadata and decode sample frames only; no editing, no narration shortening', 'elapsed_seconds': round(time.monotonic()-started, 3), 'stock_count': len(rows), 'files': rows}
    (output/'media_inventory.json').write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({k:v for k,v in report.items() if k!='files'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
