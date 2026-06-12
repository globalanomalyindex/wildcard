#!/usr/bin/env bash
# screen_concepts.sh: source-agnostic SAFETY FILTER for raw concept titles (one per line).
# Writes kept titles to stdout and a rejection log (tab: rule<TAB>title) to $2.
# The guardrail is auditable: every drop is recorded with the rule that caught it.
# Usage: screen_concepts.sh RAW_FILE REJECT_LOG > kept.txt
set -u
RAW="${1:?usage: screen_concepts.sh RAW_FILE REJECT_LOG}"
LOG="${2:?usage: screen_concepts.sh RAW_FILE REJECT_LOG}"
: > "$LOG"

deny_names='violence|war|weapon|gun|rifle|missile|bomb|nuclear|massacre|genocide|terror|murder|assassinat|suicide|self-harm|rape|sexual|porn|nud(e|ity)|slur|nazi|hitler|holocaust|slavery|lynch|abortion|election|president|senator|parliament|communis|fascis|jihad|crusade|caliph|prophet|messiah|christ|allah|buddha|disease|cancer|tumor|pandemic|overdose|cartel|cocaine|heroin|gambl|casino'
deny_person='\b(born|footballer|politician|singer|actor|actress|rapper|king|queen|emperor|dictator|pope|saint|president|sir|dame)\b'
deny_ip='\b(inc|corp|llc|ltd|trademark|franchise|brand|disney|marvel|pixar|nintendo|pokemon|mcdonald|coca-cola)\b|star wars'

n_in=0; n_keep=0
while IFS= read -r raw; do
  line="$(printf '%s' "$raw" | sed -E 's/[[:space:]]+$//; s/^[[:space:]]+//')"
  [ -n "$line" ] || continue
  case "$line" in \#*) continue ;; esac
  n_in=$((n_in+1))
  low="$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')"
  if printf '%s' "$line" | grep -qE '\|'; then printf 'pipe\t%s\n' "$line" >> "$LOG"; continue; fi
  if printf '%s' "$low" | grep -qE '\(disambiguation\)|^list of|^index of|^outline of|^history of'; then printf 'meta\t%s\n' "$line" >> "$LOG"; continue; fi
  if [ "${#line}" -gt 50 ]; then printf 'toolong\t%s\n' "$line" >> "$LOG"; continue; fi
  if printf '%s' "$low" | grep -qE "$deny_names"; then printf 'names\t%s\n' "$line" >> "$LOG"; continue; fi
  if printf '%s' "$low" | grep -qE "$deny_person"; then printf 'person\t%s\n' "$line" >> "$LOG"; continue; fi
  if printf '%s' "$low" | grep -qE "$deny_ip"; then printf 'ip\t%s\n' "$line" >> "$LOG"; continue; fi
  printf '%s\n' "$line"
  n_keep=$((n_keep+1))
done < "$RAW"
printf 'screen: %d candidates, %d kept, %d rejected (see %s)\n' "$n_in" "$n_keep" "$((n_in-n_keep))" "$LOG" >&2
