#!/usr/bin/env python3
"""Independent reference for TAU Compilation ex2 (parser for L).

Written from the ex1/ex2 PDFs only (no JFlex/CUP, no team code):
  * hand-written maximal-munch lexer following ex1 section 2
  * Earley recognizer over the EBNF grammar of ex2 Table 2 (expanded to CFG)

Output rules (ex2 section 3):
  OK              valid program
  ERROR           lexical error (and no syntax error before it)
  ERROR(line)     first syntax error, line of the offending token
                  (end of input -> line of EOF position)

Usage:  ref.py FILE...          prints "<file>\t<result>" per file
        import ref; ref.judge(src)
"""
import sys

KEYWORDS = {
    'class': 'CLASS', 'nil': 'NIL', 'array': 'ARRAY', 'while': 'WHILE',
    'int': 'TYPE_INT', 'void': 'TYPE_VOID', 'extends': 'EXTENDS',
    'return': 'RETURN', 'new': 'NEW', 'if': 'IF', 'else': 'ELSE',
    'string': 'TYPE_STRING', 'and': 'AND', 'or': 'OR',
}
SINGLE = {
    '(': 'LPAREN', ')': 'RPAREN', '[': 'LBRACK', ']': 'RBRACK',
    '{': 'LBRACE', '}': 'RBRACE', ',': 'COMMA', '.': 'DOT',
    ';': 'SEMICOLON', '+': 'PLUS', '-': 'MINUS', '*': 'TIMES',
    '/': 'DIVIDE', '=': 'EQ', '<': 'LT', '>': 'GT',
}
LETTERS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
DIGITS = set('0123456789')
WS = set(' \t\r\n')
# Figure 2: letters, digits, white spaces, ( ) [ ] { } ? ! + - * / . ;
COMMENT_OK = LETTERS | DIGITS | WS | set('()[]{}?!+-*/.;')
MAX_INT = 2 ** 15 - 1


class LexError(Exception):
    pass


def lex(src):
    """Returns (tokens, lex_error, eof_line). tokens = [(kind, line)].
    On a lexical error the token list stops right before the bad token."""
    toks = []
    i, n, line = 0, len(src), 1

    def advance_over(j):
        # move i to j, counting line terminators \r\n, \r, \n
        nonlocal i, line
        k = i
        while k < j:
            c = src[k]
            if c == '\r':
                line += 1
                if k + 1 < n and src[k + 1] == '\n':
                    k += 1
            elif c == '\n':
                line += 1
            k += 1
        i = j

    try:
        while i < n:
            c = src[i]
            if c in WS:
                advance_over(i + 2 if src.startswith('\r\n', i) else i + 1)
                continue
            if src.startswith('//', i):
                j = i + 2
                while j < n and src[j] not in '\r\n':
                    if src[j] not in COMMENT_OK:
                        raise LexError('bad char in // comment')
                    j += 1
                if j >= n:
                    raise LexError('// comment not ended by newline')
                advance_over(j)          # newline itself handled as WS
                continue
            if src.startswith('/*', i):
                end = src.find('*/', i + 2)
                body = src[i + 2:] if end < 0 else src[i + 2:end]
                for ch in body:
                    if ch not in COMMENT_OK:
                        raise LexError('bad char in /* comment')
                if end < 0:
                    raise LexError('unclosed /* comment')
                advance_over(end + 2)
                continue
            if c in LETTERS:
                j = i + 1
                while j < n and (src[j] in LETTERS or src[j] in DIGITS):
                    j += 1
                word = src[i:j]
                toks.append((KEYWORDS.get(word, 'ID'), line))
                advance_over(j)
                continue
            if c in DIGITS:
                j = i + 1
                while j < n and src[j] in DIGITS:
                    j += 1
                num = src[i:j]
                if len(num) > 1 and num[0] == '0':
                    raise LexError('leading zero')
                if int(num) > MAX_INT:
                    raise LexError('int out of range')
                toks.append(('INT', line))
                advance_over(j)
                continue
            if c == '"':
                j = i + 1
                while j < n and src[j] in LETTERS:
                    j += 1
                if j < n and src[j] == '"':
                    toks.append(('STRING', line))
                    advance_over(j + 1)
                    continue
                raise LexError('bad/unclosed string')
            if src.startswith(':=', i):
                toks.append(('ASSIGN', line))
                advance_over(i + 2)
                continue
            if c in SINGLE:
                toks.append((SINGLE[c], line))
                advance_over(i + 1)
                continue
            raise LexError('illegal character %r' % c)
    except LexError:
        return toks, True, line
    return toks, False, line


# ---------------------------------------------------------------------------
# Grammar: ex2 Table 2, EBNF expanded by hand (no epsilon rules).
# Same language as the spec; lists are left-recursive and `exp binop exp` is
# written as `exp binop prim` (unambiguous) so Earley stays fast on big inputs.
# Precedence does not change which programs are accepted.
# ---------------------------------------------------------------------------
G = r"""
program   : decs
decs      : dec | decs dec
dec       : varDec | funcDec | classDec | arrayTypedef
type      : TYPE_INT | TYPE_STRING | TYPE_VOID | ID
varDec    : type ID SEMICOLON | type ID ASSIGN exp SEMICOLON | type ID ASSIGN newExp SEMICOLON
funcDec   : type ID LPAREN RPAREN LBRACE stmtList RBRACE | type ID LPAREN params RPAREN LBRACE stmtList RBRACE
params    : type ID | params COMMA type ID
stmtList  : stmt | stmtList stmt
classDec  : CLASS ID LBRACE cFields RBRACE | CLASS ID EXTENDS ID LBRACE cFields RBRACE
cFields   : cField | cFields cField
cField    : varDec | funcDec
arrayTypedef : ARRAY ID EQ type LBRACK RBRACK SEMICOLON
exp       : prim | exp binop prim
prim      : var | LPAREN exp RPAREN | callExp | INT | MINUS INT | NIL | STRING
binop     : PLUS | MINUS | TIMES | DIVIDE | LT | GT | EQ | AND | OR
newExp    : NEW type | NEW type LBRACK exp RBRACK
callExp   : ID LPAREN RPAREN | ID LPAREN args RPAREN | var DOT ID LPAREN RPAREN | var DOT ID LPAREN args RPAREN
args      : exp | args COMMA exp
var       : ID | var DOT ID | var LBRACK exp RBRACK
stmt      : varDec
          | var ASSIGN exp SEMICOLON
          | var ASSIGN newExp SEMICOLON
          | RETURN SEMICOLON
          | RETURN exp SEMICOLON
          | IF LPAREN exp RPAREN LBRACE stmtList RBRACE
          | IF LPAREN exp RPAREN LBRACE stmtList RBRACE ELSE LBRACE stmtList RBRACE
          | WHILE LPAREN exp RPAREN LBRACE stmtList RBRACE
          | callExp SEMICOLON
"""


def _load_grammar(text):
    rules, lhs = [], None
    for raw in text.strip().splitlines():
        s = raw.strip()
        if not s:
            continue
        if ':' in s.split()[1:2] or (len(s.split()) > 1 and s.split()[1] == ':'):
            lhs, rest = s.split(':', 1)
            lhs = lhs.strip()
        else:
            rest = s.lstrip('|')
        for alt in rest.split('|'):
            syms = tuple(alt.split())
            if syms:
                rules.append((lhs, syms))
    return rules


RULES = _load_grammar(G)
NONTERMS = {l for l, _ in RULES}
BY_LHS = {}
for _idx, (_l, _r) in enumerate(RULES):
    BY_LHS.setdefault(_l, []).append(_idx)
START = 'program'


def earley(kinds):
    """Returns (first_bad_index or None, accepted_at_end)."""
    n = len(kinds)
    chart = [set() for _ in range(n + 1)]
    for r in BY_LHS[START]:
        chart[0].add((r, 0, 0))
    for k in range(n + 1):
        agenda = list(chart[k])
        S = chart[k]
        while agenda:
            r, dot, org = agenda.pop()
            lhs, rhs = RULES[r]
            if dot < len(rhs):
                sym = rhs[dot]
                if sym in NONTERMS:                     # predict
                    for r2 in BY_LHS[sym]:
                        it = (r2, 0, k)
                        if it not in S:
                            S.add(it); agenda.append(it)
                    # (no nullable rules, so no magic completion needed)
            else:                                       # complete
                for (r3, d3, o3) in list(chart[org]):
                    rhs3 = RULES[r3][1]
                    if d3 < len(rhs3) and rhs3[d3] == lhs:
                        it = (r3, d3 + 1, o3)
                        if it not in S:
                            S.add(it); agenda.append(it)
        if k == n:
            break
        tok = kinds[k]
        for (r, dot, org) in S:                         # scan
            rhs = RULES[r][1]
            if dot < len(rhs) and rhs[dot] == tok:
                chart[k + 1].add((r, dot + 1, org))
        if not chart[k + 1]:
            return k, False
    acc = any(RULES[r][0] == START and dot == len(RULES[r][1]) and org == 0
              for (r, dot, org) in chart[n])
    return None, acc


def judge(src):
    toks, lexerr, eof_line = lex(src)
    bad, acc = earley([k for k, _ in toks])
    if bad is not None:
        return 'ERROR(%d)' % toks[bad][1]
    if lexerr:
        return 'ERROR'
    if not acc:
        return 'ERROR(%d)' % eof_line
    return 'OK'


def read_src(path):
    with open(path, 'rb') as f:
        return f.read().decode('latin-1')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print('%s\t%s' % (p, judge(read_src(p))))
