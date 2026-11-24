#!/bin/bash
# Precedence/associativity check (ex2 Table 1): builds a tiny parser from OUR terminal+precedence
# declarations in cup/CUP_FILE.cup and the spec's expression rules, prints each parse fully parenthesised.
cd "$(dirname "$0")/.." || exit 1
D=$(mktemp -d); mkdir -p $D/bin
python3 -I extra_tests/tools/prec.py cup/CUP_FILE.cup $D
jflex -q -d $D jflex/LEX_FILE.lex
java -jar external_jars/java-cup-11b.jar -nowarn -parser PrecParser -symbols TokenNames -destdir $D $D/PREC.cup 2>&1 | grep -E "conflicts|rror"
javac -nowarn -cp external_jars/java-cup-11b-runtime.jar -d $D/bin $D/*.java 2>&1 | grep -v ^Note
java -cp external_jars/java-cup-11b-runtime.jar:$D/bin PrecMain $D/cases.tsv | tee $D/r.txt | grep ^FAIL
echo "precedence cases: $(grep -c ^PASS $D/r.txt) passed, $(grep -c ^FAIL $D/r.txt) failed"; rm -rf $D
