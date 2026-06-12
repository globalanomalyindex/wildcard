#!/usr/bin/env bash
# audit_concepts.sh: gate the FINAL concepts.txt.
# format `concept | tier | facet` + valid tiers + dedup + min count + tier spanning +
# zero denylist hits (belt-and-suspenders re-run of the screen's families).
set -u
FILE="${1:-references/concepts.txt}"
MIN="${WILDCARD_MIN_CONCEPTS:-150}"
TIERS="everyday natural scientific abstract"
if [ ! -r "$FILE" ]; then echo "audit: cannot read $FILE" >&2; exit 1; fi
DENY='violence|war|weapon|gun|missile|bomb|nuclear|massacre|genocide|terror|murder|assassinat|suicide|rape|sexual|porn|slur|nazi|hitler|holocaust|abortion|election|jihad|prophet|christ|allah|cocaine|heroin'

awk -F' \\| ' -v MIN="$MIN" -v TIERS="$TIERS" -v DENY="$DENY" '
function inset(v,set,  a,n,i){n=split(set,a," ");for(i=1;i<=n;i++)if(a[i]==v)return 1;return 0}
/^[[:space:]]*($|#)/{next}
{
  count++
  if (NF!=3){print "ERR line "NR": expected 3 fields, got "NF" -> "$0; e++; next}
  c=$1
  if (tolower(c) ~ DENY){print "ERR line "NR": denylist hit -> "c; e++}
  if (dup[c]++){print "ERR line "NR": duplicate -> "c; e++}
  if (!inset($2,TIERS)){print "ERR line "NR": bad tier -> "$2; e++} else seen[$2]=1
}
END{
  if (count<MIN){print "ERR too few concepts: "count" < "MIN; e++}
  n=split(TIERS,a," "); for(i=1;i<=n;i++) if(!seen[a[i]]){print "ERR missing tier: "a[i]; e++}
  if (e){print "audit FAILED: "e" problem(s)"; exit 1}
  print "audit OK: "count" concepts, all tiers present, zero denylist hits"
}' "$FILE"
