#!/usr/bin/env bash
# audit_prs.sh — audit in-window PR merges for CC 2.1.154–2.1.158 tool-channel-corruption fallout.
# RUN ONLY AFTER rolling back to a clean harness (2.1.153). Run from inside the repo to audit.
# Requires: git, gh (authenticated), jq.
#
#   SINCE=2026-05-28 ME=Chris0Jeky ./audit_prs.sh      # defaults shown; ME="" = all authors
#
set -uo pipefail

SINCE="${SINCE:-2026-05-28}"          # start of the bad-harness window (Opus 4.8 / 2.1.154 GA)
ME="${ME:-Chris0Jeky}"                 # your git author name; set ME="" to include all authors
AUTHOR_ARG=(); [ -n "$ME" ] && AUTHOR_ARG=(--author="$ME")
OUT="audit_prs_$(git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '_').tsv"

echo ">> Deriving PR list from your in-window merge commits (since $SINCE)..."
PRS=$(git log --merges --since="$SINCE" "${AUTHOR_ARG[@]}" --pretty=format:'%s' \
      | grep -oiE 'pull request #[0-9]+' | grep -oE '[0-9]+' | sort -n | uniq)

if [ -z "$PRS" ]; then
  echo "No in-window PR merges found by '${ME:-anyone}'. Nothing to audit in this repo."; exit 0
fi
echo ">> $(echo "$PRS" | wc -l | tr -d ' ') PRs to check."

printf 'PR\tmergedAt\tCI\tdiff_lines\ttitle\n' > "$OUT"
for pr in $PRS; do
  info=$(gh pr view "$pr" --json number,title,mergedAt,statusCheckRollup 2>/dev/null) \
    || { printf '%s\tERR\tERR\tERR\t(gh view failed)\n' "$pr" >> "$OUT"; echo "  #$pr  gh view FAILED"; continue; }
  ci=$(printf '%s' "$info" | jq -r '
    ([.statusCheckRollup[]? | (.conclusion // .state)]) as $c
    | if   ($c|length)==0 then "NO_CHECKS"
      elif ($c | map(select(["FAILURE","ERROR","CANCELLED","TIMED_OUT","ACTION_REQUIRED","STARTUP_FAILURE"] | index(.))) | length) > 0 then "FAILED"
      elif ($c | map(select(["SUCCESS","NEUTRAL","SKIPPED"] | index(.))) | length) == ($c|length) then "PASS"
      else "PENDING" end')
  title=$(printf '%s'  "$info" | jq -r '.title')
  merged=$(printf '%s' "$info" | jq -r '.mergedAt')
  dlines=$(gh pr diff "$pr" 2>/dev/null | wc -l | tr -d ' ')
  printf '%s\t%s\t%s\t%s\t%s\n' "$pr" "$merged" "$ci" "${dlines:-?}" "$title" >> "$OUT"
  printf '  #%-5s %-9s diff=%-5s %s\n' "$pr" "$ci" "${dlines:-?}" "$title"
done

echo
echo "=== NEEDS REVIEW: CI not PASS, or empty diff (possible silent no-op) ==="
awk -F'\t' 'NR>1 && ($3!="PASS" || $4==0)' "$OUT" || true
echo
echo "Full table written to: $OUT"
echo "Next: for each flagged PR run  gh pr checks <N> ; gh pr diff <N> ; re-run its tests."
