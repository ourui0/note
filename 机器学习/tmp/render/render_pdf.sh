#!/bin/bash
# render_pdf.sh <html-file> <pdf-file>
# Headless Chromium does not always exit after writing the PDF, so poll for the
# output file and then stop the browser instead of waiting on the process.
set -u

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HTML="$1"
PDF="$2"
PROFILE="$(cd "$(dirname "$0")" && pwd)/chrome-run-$(basename "$PDF" .pdf)"

rm -rf "$PROFILE"
rm -f "$PDF"

"$CHROME" \
  --headless=old \
  --no-sandbox \
  --disable-gpu \
  --disable-crash-reporter \
  --disable-breakpad \
  --disable-background-networking \
  --disable-component-update \
  --disable-sync \
  --disable-extensions \
  --no-first-run \
  --user-data-dir="$PROFILE" \
  --no-pdf-header-footer \
  --print-to-pdf="$PDF" \
  "file://$HTML" >/dev/null 2>&1 &
PID=$!

for _ in $(seq 1 90); do
  if [ -s "$PDF" ]; then
    sleep 2                 # let the writer flush
    kill "$PID" 2>/dev/null
    wait "$PID" 2>/dev/null
    echo "OK $(stat -f%z "$PDF") bytes  $(basename "$PDF")"
    exit 0
  fi
  sleep 1
done

kill "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
echo "FAILED: no PDF written for $HTML"
exit 1
