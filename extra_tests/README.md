# Extra tests for ex2

These are not part of the submission. Leave `extra_tests/` out of the zip.

Run everything from the `ex2` directory after `make`:

```sh
bash extra_tests/run_extra_tests.sh   # 329 hand-written tests in the course format
bash extra_tests/prec.sh              # 45 precedence/associativity checks (Table 1)
bash extra_tests/fuzz.sh 1000 10 1    # 11,000 random programs + mutants vs. an independent reference
```

## Hand-written tests (`input/`, `expected_output/`)

The expected outputs were set by hand from the ex1/ex2 PDFs. They were then cross-checked against `tools/ref.py`, which agrees on all 329.

| Prefix | What | Count |
|---|---|---|
| A | valid declarations (types, init forms, `new`, typedefs, classes, extends, methods) | 25 |
| B | valid statements (every stmt form, nesting, call/assign targets) | 20 |
| C | valid expressions (all operators, chains, negatives, calls, var chains) | 20 |
| D | valid lexical corner cases (keyword-prefixed IDs, odd comments, CRLF / CR-only, no whitespace) | 18 |
| E | syntax errors in declarations | 50 |
| F | syntax errors in statements | 50 |
| G | syntax errors in expressions (`-x`, `f().g`, `(a)[1]`, `a*/b`, `0x10`, ...) | 48 |
| H | lexical errors: output must be plain `ERROR` | 50 |
| I | error line numbers (blank lines, comments, CRLF, CR, mixed, EOF) | 21 |
| J | first error wins (syntax error before lexical error, and vice versa) | 12 |
| K | stress: 2000 functions, depth 300/500/1000 nesting, 20000 statements, 5000-line files | 15 |

Names containing `EOF` depend on the line reported for a syntax error at end of input. We use the line the lexer is on at EOF, the same as the skeleton's `lexer.getLine()`. That means a missing `}` in a file that ends with `\n` is reported one line after the last line. The PDF doesn't say which line to use, so treat those tests as our convention.

## Tools (`tools/`)

- `ref.py` is an independent reference written from the PDFs only: a hand-written lexer plus an Earley recognizer over the Table 2 grammar. It shares no code with our JFlex/CUP files.
- `fuzz.py` generates random valid programs. It then mutates them, either at token level (delete, duplicate, swap, insert, replace) or at character level (bad chars, leading zeros, big ints, bad strings, bad or unclosed comments).
- `BatchRun.java` runs `Main` on thousands of files inside one JVM.
- `prec.py` builds the precedence-check grammar for `prec.sh`.
- `tests.py` regenerates `input/` and `expected_output/`.
