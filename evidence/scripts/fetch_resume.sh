#!/usr/bin/env bash
# Resume-capable fetch for NHANES files the CDC server keeps cutting off.
# Usage: fetch_resume.sh <raw_dir> <year> <file> [<year> <file> ...]
RAW="$1"; shift
while [ $# -ge 2 ]; do
  yr="$1"; f="$2"; shift 2
  u="https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/$yr/DataFiles/$f"
  dest="$RAW/nhanes/$yr/$f"
  [ -s "$dest" ] && { echo "have $dest"; continue; }
  exp=$(curl -sSI --max-time 30 "$u" | awk 'tolower($1)=="content-length:"{print $2}' | tr -d '\r')
  for i in $(seq 1 30); do
    curl -sSL -C - --max-time 300 -o "$dest.resume" "$u" 2>/dev/null
    got=$(stat -f%z "$dest.resume" 2>/dev/null || echo 0)
    [ "$got" = "$exp" ] && break
  done
  got=$(stat -f%z "$dest.resume" 2>/dev/null || echo 0)
  if [ "$got" = "$exp" ]; then mv "$dest.resume" "$dest"; echo "ok   $dest ($got bytes)"; else echo "FAIL $dest ($got of $exp)"; fi
done
