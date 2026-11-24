#!/bin/bash
# Run the extra hand-written tests against ./PARSER (run from the ex2 directory after `make`).
#   bash extra_tests/run_extra_tests.sh          -> summary per category + failures
cd "$(dirname "$0")/.." || exit 1
[ -f PARSER ] || { echo "PARSER not found - run make first"; exit 1; }
T=extra_tests; O=$(mktemp -d); pass=0; fail=0
declare -A tot ok
for f in $T/input/TEST_*.txt; do
  b=$(basename "$f" .txt); c=${b:5:1}
  timeout 10 java -jar PARSER "$f" "$O/$b.txt" >/dev/null 2>&1
  exp=$(cat "$T/expected_output/${b}_Expected_Output.txt"); got=$(cat "$O/$b.txt" 2>/dev/null || echo '<no output>')
  tot[$c]=$(( ${tot[$c]:-0} + 1 ))
  if [ "$exp" == "$got" ]; then pass=$((pass+1)); ok[$c]=$(( ${ok[$c]:-0} + 1 ))
  else fail=$((fail+1)); echo "FAIL $b: expected $exp, got $got"; fi
done
for c in A B C D E F G H I J K; do printf "%s %3d/%-3d " $c ${ok[$c]:-0} ${tot[$c]:-0}; done; echo
echo "TOTAL: $pass passed, $fail failed"; rm -rf "$O"; [ $fail -eq 0 ]
