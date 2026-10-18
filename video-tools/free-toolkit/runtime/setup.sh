#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CACHE_DIR="${GUMA_NPM_CACHE:-/workspace/guma-video/tooling/npm-cache}"
mkdir -p "$CACHE_DIR"
cd "$TASK_DIR"
command -v node >/dev/null
command -v npm >/dev/null
node -e 'if (Number(process.versions.node.split(".")[0]) < 20) throw new Error("Node 20 veya üstü gerekli")'
npm --cache "$CACHE_DIR" ci --no-fund
node scripts/licenses.mjs
printf '%s\n' 'Kurulum tamamlandı. Kamera testi: npm run proof:stills'
