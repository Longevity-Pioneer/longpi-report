#!/usr/bin/env bash
# Download every public dataset the LongPi evidence pipeline uses.
# Re-runnable: files that already exist are skipped.
#
#   UN World Population Prospects 2024, complete (single-age) life tables, medium variant
#     https://population.un.org/wpp/  (licence: CC BY 3.0 IGO)
#   NHANES 1999-2018 public-use files (CDC/NCHS, public domain)
#   NHANES public-use Linked Mortality Files, follow-up to 2019-12-31 (CDC/NCHS)
#   NHANES 1999-2002 DNA methylation epigenetic biomarkers, released 2024-07-31 (CDC/NCHS)
#
# Usage: fetch_public_data.sh <raw_dir>
set -u
RAW="${1:?usage: fetch_public_data.sh <raw_dir>}"
mkdir -p "$RAW/wpp2024" "$RAW/nhanes" "$RAW/nhanes_mort" "$RAW/nhanes_dnam"

get() {  # get <url> <dest>
  local url="$1" dest="$2"
  if [ -s "$dest" ]; then return 0; fi
  curl -fsSL --retry 4 --retry-delay 3 --max-time 1800 -o "$dest.part" "$url" && mv "$dest.part" "$dest" \
    && echo "ok   $dest" || { echo "FAIL $url"; rm -f "$dest.part"; }
}

# ---- UN WPP 2024 life tables (China is extracted later by build_china_lifetable.py)
WPP="https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES"
for sex in Male Female; do
  for span in 1950-2023 2024-2100; do
    get "$WPP/WPP2024_Life_Table_Complete_Medium_${sex}_${span}.csv.gz" "$RAW/wpp2024/WPP2024_Life_Table_Complete_Medium_${sex}_${span}.csv.gz" &
  done
done

# ---- NHANES continuous cycles
NH="https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public"
common_q="DEMO BPX BMX SMQ PAQ ALQ DIQ MCQ BPQ"
files_for() {  # bash 3.2 (macOS) has no associative arrays
  case "$1" in
    1999) echo "$common_q LAB18 LAB25 LAB11 LAB10 LAB13 LAB13AM LAB10AM CVX" ;;
    2001|2003) echo "$common_q L40 L25 L11 L10 L13 L13AM L10AM CVX" ;;
    2005|2007|2009) echo "$common_q SLQ BIOPRO CBC CRP GHB TCHOL HDL TRIGLY GLU" ;;
    2011|2013) echo "$common_q SLQ BIOPRO CBC GHB TCHOL HDL TRIGLY GLU MGX" ;;
    2015|2017) echo "$common_q SLQ BIOPRO CBC HSCRP GHB TCHOL HDL TRIGLY GLU" ;;
  esac
}
suffix_for() {
  case "$1" in
    1999) echo "" ;; 2001) echo "_B" ;; 2003) echo "_C" ;; 2005) echo "_D" ;; 2007) echo "_E" ;;
    2009) echo "_F" ;; 2011) echo "_G" ;; 2013) echo "_H" ;; 2015) echo "_I" ;; 2017) echo "_J" ;;
  esac
}

for yr in 1999 2001 2003 2005 2007 2009 2011 2013 2015 2017; do
  mkdir -p "$RAW/nhanes/$yr"
  suf="$(suffix_for "$yr")"
  for stem in $(files_for "$yr"); do
    f="${stem}${suf}.xpt"
    get "$NH/$yr/DataFiles/$f" "$RAW/nhanes/$yr/$f"
  done
done

# ---- Linked mortality (public-use, through 2019)
LM="https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality"
for span in 1999_2000 2001_2002 2003_2004 2005_2006 2007_2008 2009_2010 2011_2012 2013_2014 2015_2016 2017_2018; do
  get "$LM/NHANES_${span}_MORT_2019_PUBLIC.dat" "$RAW/nhanes_mort/NHANES_${span}_MORT_2019_PUBLIC.dat"
done
get "$LM/NHANES_III_MORT_2019_PUBLIC.dat" "$RAW/nhanes_mort/NHANES_III_MORT_2019_PUBLIC.dat"

# ---- DNA methylation epigenetic biomarkers, NHANES 1999-2002 adults 50+ (public file and documentation)
DN="https://wwwn.cdc.gov/nchs/data/nhanes/dnam"
get "$DN/dnmepi.sas7bdat" "$RAW/nhanes_dnam/dnmepi.sas7bdat"
get "$DN/NHANES%20DNAm%20Epigenetic%20Biomarkers%20Data%20Documentation.pdf" "$RAW/nhanes_dnam/dnam_doc.pdf"

wait
echo "done"
