#!/usr/bin/env bash
set -euo pipefail
SOURCE=${1:-../runtime-generated-bake/out/production-540-lowfps.mp4}
OUTPUT=${2:-public/production-camera.mp4}
INTERMEDIATE="${OUTPUT}.intermediate.mp4"
trap 'rm -f "$INTERMEDIATE"' EXIT
ffmpeg -y -hide_banner -loglevel warning -i "$SOURCE" \
  -vf "setpts=1.421*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:me=hexbs:vsbmc=1,scale=720:1280:flags=lanczos" \
  -an -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p "$INTERMEDIATE"
# Motion interpolation may omit the last source interval at EOF. Pad separately
# so the source movie covers the complete planned 14.21-second film section.
ffmpeg -y -hide_banner -loglevel warning -i "$INTERMEDIATE" \
  -vf "tpad=stop_mode=clone:stop_duration=2" -t 14.233333 -r 30 \
  -an -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -movflags +faststart "$OUTPUT"
