#!/usr/bin/env bash
# Serialize Qt sessions sharing one Wine prefix; use a real CJK font fixture.
set -euo pipefail
rouge_wine_launcher="${ROUGE_WINE_PYTHON_LAUNCHER:-/workspace/.compat/run-wine-python.sh}"
if ! test -x "$rouge_wine_launcher"; then
  echo 'The configured Wine compatibility Python launcher is unavailable.' >&2
  exit 1
fi
if test -z "${ROUGE_TEST_CJK_FONT:-}" && test -f /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc; then
  export ROUGE_TEST_CJK_FONT='Z:\usr\share\fonts\opentype\noto\NotoSansCJK-Regular.ttc'
fi
exec flock /tmp/rouge-wine-python.lock "$rouge_wine_launcher" "$@"
