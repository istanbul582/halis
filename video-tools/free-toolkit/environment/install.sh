set -euo pipefail
PROJECT_DIR=""
for CANDIDATE in /workspace/halis /workspace; do
  if [ -f "$CANDIDATE/video-tools/free-toolkit/runtime/package-lock.json" ]; then
    PROJECT_DIR="$CANDIDATE"
    break
  fi
done
if [ -z "$PROJECT_DIR" ]; then
  printf '%s\n' 'Video toolkit checkout is missing under /workspace/halis or /workspace.' >&2
  exit 1
fi
for BIN in node npm python3 chromium ffmpeg ffprobe blender; do
  command -v "$BIN" >/dev/null
done
export GUMA_NPM_CACHE=/workspace/guma-video/tooling/npm-cache
bash "$PROJECT_DIR/video-tools/free-toolkit/runtime/setup.sh"
bash "$PROJECT_DIR/video-tools/free-toolkit/analysis-tools/setup.sh"
"$PROJECT_DIR/video-tools/free-toolkit/analysis-tools/.venv/bin/python" -m pip --no-cache-dir check
"$PROJECT_DIR/video-tools/free-toolkit/analysis-tools/.venv/bin/python" -c 'import cv2, scipy.signal, scenedetect, opentimelineio; print("Video analysis, timeline and audio DSP imports passed")'

FILM_DIR="$PROJECT_DIR/video-tools/free-toolkit/film"
if [ -d "$FILM_DIR" ] && [ ! -e "$FILM_DIR/node_modules" ] && [ ! -L "$FILM_DIR/node_modules" ]; then
  ln -s ../runtime/node_modules "$FILM_DIR/node_modules"
fi
