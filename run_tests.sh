#!/bin/sh

for f in input/TEST*; do
    name=$(basename "$f")
    exp="expected_output/${name%.txt}_Expected_Output.txt"
    java -jar PARSER "$f" "output/$name" > /dev/null 2>&1
    diff -u "$exp" "output/$name" && echo "PASS: $name" || echo "FAIL: $name"
done
