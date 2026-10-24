#!/usr/bin/env bash
# Parallel NHANES fetch (complements fetch_public_data.sh; same destinations, separate temp names).
# Usage: fetch_nhanes_parallel.sh <raw_dir>
RAW="${1:?raw dir}"
NH="https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public"
common_q="DEMO BPX BMX SMQ PAQ ALQ DIQ MCQ BPQ"
list() {
  for yr in 2017 2015 2013 2011 2009 2007 2005 2003 2001 1999; do
    case "$yr" in
      1999) suf=""; fl="$common_q LAB18 LAB25 LAB11 LAB10 LAB13 LAB13AM LAB10AM CVX" ;;
      2001) suf="_B"; fl="$common_q L40 L25 L11 L10 L13 L13AM L10AM CVX" ;;
      2003) suf="_C"; fl="$common_q L40 L25 L11 L10 L13 L13AM L10AM CVX" ;;
      2005) suf="_D"; fl="$common_q SLQ BIOPRO CBC CRP GHB TCHOL HDL TRIGLY GLU" ;;
      2007) suf="_E"; fl="$common_q SLQ BIOPRO CBC CRP GHB TCHOL HDL TRIGLY GLU" ;;
      2009) suf="_F"; fl="$common_q SLQ BIOPRO CBC CRP GHB TCHOL HDL TRIGLY GLU" ;;
      2011) suf="_G"; fl="$common_q SLQ BIOPRO CBC GHB TCHOL HDL TRIGLY GLU MGX" ;;
      2013) suf="_H"; fl="$common_q SLQ BIOPRO CBC GHB TCHOL HDL TRIGLY GLU MGX" ;;
      2015) suf="_I"; fl="$common_q SLQ BIOPRO CBC HSCRP GHB TCHOL HDL TRIGLY GLU" ;;
      2017) suf="_J"; fl="$common_q SLQ BIOPRO CBC HSCRP GHB TCHOL HDL TRIGLY GLU" ;;
    esac
    mkdir -p "$RAW/nhanes/$yr"
    for s in $fl; do echo "$yr ${s}${suf}.xpt"; done
  done
}
list | xargs -P 6 -n 2 sh -c '
  yr="$1"; f="$2"; dest="'"$RAW"'/nhanes/$yr/$f"
  [ -s "$dest" ] && exit 0
  curl -fsSL --retry 5 --retry-delay 3 --max-time 900 -o "$dest.p2" "'"$NH"'/$yr/DataFiles/$f" && mv "$dest.p2" "$dest" && echo "ok   $dest" || { echo "FAIL $f"; rm -f "$dest.p2"; }
' _
echo done
