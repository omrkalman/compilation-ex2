#!/bin/bash
# Differential fuzzing: random valid L programs + token/char mutants, PARSER vs tools/ref.py.
#   bash extra_tests/fuzz.sh [N_VALID=1000] [MUTANTS_PER_PROGRAM=10] [SEED=1]   (needs python3, javac)
cd "$(dirname "$0")/.." || exit 1
N=${1:-1000}; M=${2:-10}; S=${3:-1}; FZ=$(mktemp -d); H=$FZ/h
python3 -I extra_tests/tools/fuzz.py $FZ $N $M $S || exit 1
javac -nowarn -cp PARSER -d $H extra_tests/tools/BatchRun.java 2>&1 | grep -v ^Note
java -Xss16m -cp PARSER:$H BatchRun $FZ/list.tsv
python3 -I - $FZ <<'PY'
import sys, os, collections
fz = sys.argv[1]; tot = collections.Counter(); bad = []
for line in open(fz + '/expected.tsv'):
    name, exp, kind = line.rstrip('\n').split('\t')
    p = fz + '/out/' + name + '.txt'
    got = open(p).read() if os.path.exists(p) else '<missing>'
    k = 'OK' if exp == 'OK' else ('LEXICAL' if exp == 'ERROR' else 'SYNTAX')
    tot[k] += 1
    if got != exp: bad.append('%s (%s): expected %s got %s  [input kept in %s/in]' % (name, kind, exp, got, fz))
print(', '.join('%s %d' % kv for kv in sorted(tot.items())), '| mismatches:', len(bad))
print('\n'.join(bad[:20]))
PY
