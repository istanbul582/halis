#!/usr/bin/env bash
set -euo pipefail
VIDEO_INPUT=${1:-out/GUMA_v5_full.mp4}
PIXEL_FORMAT=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of default=noprint_wrappers=1:nokey=1 "$VIDEO_INPUT")
INPUT_RANGE=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_range -of default=noprint_wrappers=1:nokey=1 "$VIDEO_INPUT")
INPUT_MATRIX=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_space -of default=noprint_wrappers=1:nokey=1 "$VIDEO_INPUT")
printf 'Input: pixel=%s range=%s matrix=%s\n' "$PIXEL_FORMAT" "$INPUT_RANGE" "$INPUT_MATRIX"
if [[ "$PIXEL_FORMAT" == yuv420p && "$INPUT_RANGE" == tv ]]; then
  python verify_film.py "$VIDEO_INPUT"
  exit 0
fi
if [[ "$PIXEL_FORMAT" != yuvj420p || "$INPUT_RANGE" != pc || "$INPUT_MATRIX" != bt470bg ]]; then
  printf 'Unexpected input color tags; review conversion instead of guessing.\n' >&2
  exit 1
fi
VIDEO_CANDIDATE="${VIDEO_INPUT%.mp4}-compatible.mp4"
# scale's default in_color_matrix=auto reads the actual bt470bg source tag.
# out_color_matrix=bt709 converts YUV coefficients as well as full->limited range.
ffmpeg -y -hide_banner -loglevel warning -i "$VIDEO_INPUT" -map 0:v:0 -map 0:a:0 \
  -vf "scale=in_range=full:out_range=limited:out_color_matrix=bt709,format=yuv420p" \
  -c:v libx264 -preset veryfast -crf 18 -threads 4 -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a copy -movflags +faststart "$VIDEO_CANDIDATE"
python verify_film.py "$VIDEO_CANDIDATE"
mv "$VIDEO_CANDIDATE" "$VIDEO_INPUT"
python - "$VIDEO_INPUT" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);report=p.with_name('FINAL_VERIFICATION.json')
d=json.loads(report.read_text());d['file']=str(p.resolve());report.write_text(json.dumps(d,ensure_ascii=False,indent=2))
PY
