#!/usr/bin/env bash
# Official Entrypoint Contract: ./run.sh <video.mp4> <out.json>
set -e

if [ "$#" -lt 2 ]; then
    echo "Usage: ./run.sh <video.mp4> <out.json>"
    exit 1
fi

VIDEO_PATH="$1"
OUTPUT_JSON="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

python3 -m inference.cli "${VIDEO_PATH}" "${OUTPUT_JSON}"

