#!/usr/bin/env bash
# Thin shim: all real logic lives in start.py so macOS, Linux, and Windows
# share one launcher. See ./start.py --help.
exec python3 "$(cd "$(dirname "$0")" && pwd)/start.py" "$@"
