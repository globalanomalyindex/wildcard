#!/usr/bin/env bash
# Audit the knowledge map: size, format, valid axis tokens, full bucket coverage, no dupes.
# Usage: audit_domains.sh [FILE]   (default references/domains.txt)
#   WILDCARD_MIN_DOMAINS overrides the minimum leaf count (default 250).
set -u
FILE="${1:-references/domains.txt}"
MIN="${WILDCARD_MIN_DOMAINS:-250}"
if [ ! -r "$FILE" ]; then echo "audit: cannot read $FILE" >&2; exit 1; fi

SCALES="quantum molecular human ecological geological cosmic"
MEDIA="living mineral fluid social symbolic mechanical"
ACTS="measuring building healing performing governing preserving"
ERAS="ancient-craft industrial contemporary frontier"

awk -F' \\| ' -v MIN="$MIN" \
    -v SCALES="$SCALES" -v MEDIA="$MEDIA" -v ACTS="$ACTS" -v ERAS="$ERAS" '
function inset(v, set,   a,n,i){ n=split(set,a," "); for(i=1;i<=n;i++) if(a[i]==v) return 1; return 0 }
function mark(axis,v){ seen[axis SUBSEP v]=1 }
BEGIN{ errors=0 }
/^[[:space:]]*($|#)/ { next }
{
  count++
  if (NF != 5) { print "ERR line " NR ": expected 5 fields, got " NF " -> " $0; errors++; next }
  dom=$1
  if (dom ~ /\|/) { print "ERR line " NR ": domain contains pipe -> " dom; errors++ }
  if (dups[dom]++) { print "ERR line " NR ": duplicate domain -> " dom; errors++ }
  if (!inset($2,SCALES)) { print "ERR line " NR ": bad scale -> " $2; errors++ } else mark("scale",$2)
  if (!inset($3,MEDIA))  { print "ERR line " NR ": bad medium -> " $3; errors++ } else mark("medium",$3)
  if (!inset($4,ACTS))   { print "ERR line " NR ": bad activity -> " $4; errors++ } else mark("activity",$4)
  if (!inset($5,ERAS))   { print "ERR line " NR ": bad era -> " $5; errors++ } else mark("era",$5)
}
END{
  if (count < MIN) { print "ERR too few domains: " count " < " MIN; errors++ }
  # every bucket of every axis must appear at least once (spanning)
  na=split(SCALES,A," "); for(i=1;i<=na;i++) if(!seen["scale" SUBSEP A[i]]) { print "ERR missing scale bucket: " A[i]; errors++ }
  na=split(MEDIA,A," ");  for(i=1;i<=na;i++) if(!seen["medium" SUBSEP A[i]]) { print "ERR missing medium bucket: " A[i]; errors++ }
  na=split(ACTS,A," ");   for(i=1;i<=na;i++) if(!seen["activity" SUBSEP A[i]]) { print "ERR missing activity bucket: " A[i]; errors++ }
  na=split(ERAS,A," ");   for(i=1;i<=na;i++) if(!seen["era" SUBSEP A[i]]) { print "ERR missing era bucket: " A[i]; errors++ }
  if (errors==0) { print "audit OK: " count " domains, all axes span every bucket"; exit 0 }
  print "audit FAILED: " errors " problem(s)"; exit 1
}
' "$FILE"
