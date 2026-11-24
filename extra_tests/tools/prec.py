#!/usr/bin/env python3
"""Precedence/associativity check of a team CUP file against ex2 Table 1.

Builds PREC.cup = the team's own `terminal` + `precedence` declarations
+ the spec's exp/var/callExp rules with actions that print a fully
parenthesised form. Usage: prec.py CUP_FILE OUTDIR  -> writes PREC.cup, PrecMain.java, cases.tsv
"""
import re, sys, os

CASES = [  # (expression, expected parenthesisation per Table 1)
    ('a + b * c', '(a+(b*c))'),
    ('a * b + c', '((a*b)+c)'),
    ('a - b - c', '((a-b)-c)'),
    ('a - b + c', '((a-b)+c)'),
    ('a + b - c', '((a+b)-c)'),
    ('a / b / c', '((a/b)/c)'),
    ('a / b * c', '((a/b)*c)'),
    ('a * b / c', '((a*b)/c)'),
    ('a * b * c', '((a*b)*c)'),
    ('a < b > c', '((a<b)>c)'),
    ('a > b < c', '((a>b)<c)'),
    ('a = b = c', '((a=b)=c)'),
    ('a < b = c', '((a<b)=c)'),
    ('a = b < c', '(a=(b<c))'),
    ('a < b + c', '(a<(b+c))'),
    ('a + b < c - d', '((a+b)<(c-d))'),
    ('a or b and c', '(a or (b and c))'),
    ('a and b or c', '((a and b) or c)'),
    ('a or b or c', '((a or b) or c)'),
    ('a and b and c', '((a and b) and c)'),
    ('a = b and c = d', '((a=b) and (c=d))'),
    ('a and b = c', '(a and (b=c))'),
    ('a or b < c', '(a or (b<c))'),
    ('a - b * c + d / e', '((a-(b*c))+(d/e))'),
    ('(a + b) * c', '((a+b)*c)'),
    ('a * (b + c)', '(a*(b+c))'),
    ('a + b.f()', '(a+(b.f()))'),
    ('a + b.f() * c', '(a+((b.f())*c))'),
    ('a + b[1] * c', '(a+((b[1])*c))'),
    ('a.b.c', '((a.b).c)'),
    ('a[1][2]', '((a[1])[2])'),
    ('a.b[1].c', '(((a.b)[1]).c)'),
    ('a[i + 1] * 2', '((a[(i+1)])*2)'),
    ('a.b.f(1)', '((a.b).f(1))'),
    ('f(a + b * c, d)', 'f((a+(b*c)),d)'),
    ('-1 - 2', '(-1-2)'),
    ('1 - -2', '(1--2)'),
    ('-1 * -2 + -3', '((-1*-2)+-3)'),
    ('a > b + c * d = e or f and g < h', '(((a>(b+(c*d)))=e) or (f and (g<h)))'),
    ('a - b - c - d - e', '((((a-b)-c)-d)-e)'),
    ('a / b * c / d', '(((a/b)*c)/d)'),
    ('a + b - c + d', '(((a+b)-c)+d)'),
    ('a * b / c * d', '(((a*b)/c)*d)'),
    ('a > b < c > d', '(((a>b)<c)>d)'),
    ('nil = a.f(b[2].c)', '(nil=(a.f(((b[2]).c))))'),
]

OPS = [('PLUS', '+'), ('MINUS', '-'), ('TIMES', '*'), ('DIVIDE', '/'), ('LT', '<'),
       ('GT', '>'), ('EQ', '='), ('AND', ' and '), ('OR', ' or ')]


def main():
    cup, out = sys.argv[1], sys.argv[2]
    src = open(cup, encoding='utf-8', errors='replace').read()
    terms = [l for l in src.splitlines() if re.match(r'\s*terminal\b', l)]
    precs = [l for l in src.splitlines() if re.match(r'\s*precedence\b', l)]
    g = ['import java_cup.runtime.*;', ''] + terms + [
        'non terminal String top, exp, var, callExp, args;'] + precs + ['start with top;', '',
        'top ::= exp:e {: RESULT = e; :};', 'exp ::= var:v {: RESULT = v; :}',
        '  | LPAREN exp:e RPAREN {: RESULT = e; :}']
    for tok, sym in OPS:
        g.append('  | exp:a %s exp:b {: RESULT = "(" + a + "%s" + b + ")"; :}' % (tok, sym))
    g += ['  | callExp:c {: RESULT = c; :}',
          '  | INT:i {: RESULT = "" + i; :}',
          '  | MINUS INT:i {: RESULT = "-" + i; :}',
          '  | NIL {: RESULT = "nil"; :}',
          '  | STRING {: RESULT = "str"; :}', '  ;',
          'var ::= ID:n {: RESULT = n; :}',
          '  | var:v DOT ID:n {: RESULT = "(" + v + "." + n + ")"; :}',
          '  | var:v LBRACK exp:e RBRACK {: RESULT = "(" + v + "[" + e + "])"; :}', '  ;',
          'callExp ::= ID:f LPAREN args:a RPAREN {: RESULT = f + "(" + a + ")"; :}',
          '  | ID:f LPAREN RPAREN {: RESULT = f + "()"; :}',
          '  | var:v DOT ID:f LPAREN args:a RPAREN {: RESULT = "(" + v + "." + f + "(" + a + "))"; :}',
          '  | var:v DOT ID:f LPAREN RPAREN {: RESULT = "(" + v + "." + f + "())"; :}', '  ;',
          'args ::= exp:e {: RESULT = e; :} | args:a COMMA exp:e {: RESULT = a + "," + e; :};']
    os.makedirs(out, exist_ok=True)
    open(out + '/PREC.cup', 'w').write('\n'.join(g) + '\n')
    open(out + '/cases.tsv', 'w').write(''.join('%s\t%s\n' % c for c in CASES))
    open(out + '/PrecMain.java', 'w').write('''import java.io.*;
import java.nio.file.*;
public class PrecMain {
  public static void main(String[] a) throws Exception {
    PrintStream real = System.out;
    for (String line : Files.readAllLines(Paths.get(a[0]))) {
      String[] p = line.split("\\t");
      String got;
      try {
        System.setOut(new PrintStream(OutputStream.nullOutputStream()));
        got = (String) new PrecParser(new Lexer(new StringReader(p[0]))).parse().value;
      } catch (Throwable t) { got = "<parse error>"; }
      System.setOut(real);
      real.println((got.equals(p[1]) ? "PASS " : "FAIL ") + p[0] + "   expected " + p[1] + "   got " + got);
    }
  }
}
''')


if __name__ == '__main__':
    main()
