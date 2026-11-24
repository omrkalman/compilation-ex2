#!/usr/bin/env python3
"""Generate random L programs (valid by construction) and mutants of them.

Usage: fuzz.py OUTDIR N_VALID MUTANTS_PER_VALID SEED
Writes OUTDIR/in/*.txt, OUTDIR/expected.tsv (name<TAB>ref result<TAB>kind)
and OUTDIR/list.tsv for BatchRun.
"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ref

KW = set(ref.KEYWORDS)
R = None


def ident():
    while True:
        n = R.choice(['a', 'b', 'x', 'y', 'i', 'j', 'len', 'list', 'head', 'tail',
                      'Node', 'Father', 'Son', 'arr', 'mat', 'f', 'g', 'foo',
                      'printInt', 'printString', 'p' + str(R.randint(0, 99)),
                      'I' + 'n' * R.randint(1, 3) + 't', 'whilex', 'ifs', 'newA',
                      'classy', 'nil0', 'orr', 'andy', 'returnZ', 'voidy'])
        if n not in KW:
            return [n]


def intlit():
    return [str(R.choice([0, 1, 2, 7, 10, 99, 100, 255, 1000, 32766, 32767,
                          R.randint(0, 32767)]))]


def strlit():
    return ['"' + ''.join(R.choice('abcXYZq') for _ in range(R.randint(0, 6))) + '"']


def typ():
    return R.choice([['int'], ['string'], ['void'], ident()])


def var(d):
    c = R.random()
    if d <= 0 or c < 0.5:
        return ident()
    if c < 0.75:
        return var(d - 1) + ['.'] + ident()
    return var(d - 1) + ['['] + exp(d - 1) + [']']


def args(d):
    out = exp(d)
    for _ in range(R.choice([0, 0, 1, 2, 3])):
        out += [','] + exp(d)
    return out


def call(d):
    a = args(d - 1) if R.random() < 0.7 else []
    if R.random() < 0.5:
        return ident() + ['('] + a + [')']
    return var(d - 1) + ['.'] + ident() + ['('] + a + [')']


def leaf():
    return R.choice([ident, intlit, lambda: ['-'] + intlit(), lambda: ['nil'], strlit])()


def exp(d):
    if d <= 0:
        return leaf()
    c = R.random()
    if c < 0.2:
        return leaf()
    if c < 0.35:
        return var(d - 1)
    if c < 0.45:
        return ['('] + exp(d - 1) + [')']
    if c < 0.8:
        op = R.choice(['+', '-', '*', '/', '<', '>', '=', 'and', 'or'])
        return exp(d - 1) + [op] + exp(d - 1)
    return call(d)


def newexp(d):
    if R.random() < 0.5:
        return ['new'] + typ()
    return ['new'] + typ() + ['['] + exp(d) + [']']


def vardec(d):
    c = R.random()
    head = typ() + ident()
    if c < 0.35:
        return head + [';']
    if c < 0.75:
        return head + [':='] + exp(d) + [';']
    return head + [':='] + newexp(d) + [';']


def stmts(d):
    out = []
    for _ in range(R.randint(1, 4 if d > 0 else 2)):
        out += stmt(d)
    return out


def stmt(d):
    c = R.random()
    if d <= 0:
        c = R.choice([0.05, 0.2, 0.45, 0.9])
    if c < 0.12:
        return vardec(d)
    if c < 0.35:
        return var(d) + [':='] + exp(d) + [';']
    if c < 0.42:
        return var(d) + [':='] + newexp(d) + [';']
    if c < 0.5:
        return ['return', ';'] if R.random() < 0.3 else ['return'] + exp(d) + [';']
    if c < 0.6:
        return ['if', '('] + exp(d) + [')', '{'] + stmts(d - 1) + ['}']
    if c < 0.68:
        return (['if', '('] + exp(d) + [')', '{'] + stmts(d - 1) + ['}', 'else', '{']
                + stmts(d - 1) + ['}'])
    if c < 0.78:
        return ['while', '('] + exp(d) + [')', '{'] + stmts(d - 1) + ['}']
    return call(d) + [';']


def funcdec(d):
    ps = []
    for k in range(R.choice([0, 0, 1, 2, 3])):
        ps += ([','] if k else []) + typ() + ident()
    return typ() + ident() + ['('] + ps + [')', '{'] + stmts(d) + ['}']


def classdec(d):
    out = ['class'] + ident()
    if R.random() < 0.4:
        out += ['extends'] + ident()
    out += ['{']
    for _ in range(R.randint(1, 3)):
        out += vardec(d) if R.random() < 0.5 else funcdec(d)
    return out + ['}']


def program(d):
    out = []
    for _ in range(R.randint(1, 5)):
        out += R.choice([vardec, funcdec, funcdec, classdec,
                         lambda d: ['array'] + ident() + ['='] + typ() + ['[', ']', ';']])(d)
    return out


PUNCT = set('()[]{};,')


def render(toks):
    """Join tokens with random (always safe) whitespace / legal comments."""
    out = []
    for i, t in enumerate(toks):
        if i:
            prev = toks[i - 1]
            r = R.random()
            if (prev in PUNCT or t in PUNCT) and r < 0.3 and prev != '/' and t not in ('/', '*'):
                sep = ''
            elif r < 0.55:
                sep = ' '
            elif r < 0.8:
                sep = R.choice(['\n', '\r\n', '\n    ', '\n\t', '\n\n'])
            elif r < 0.9:
                sep = R.choice(['\t', '  '])
            elif r < 0.95:
                sep = ' /* ' + R.choice(['ok', 'x + y', 'a*b?', '(1)!', 'multi\nline;', '[]{}.']) + ' */ '
            else:
                sep = ' // ' + R.choice(['note', 'x + y - 1;', 'q?!', '']) + '\n'
            out.append(sep)
        out.append(t)
    out.append(R.choice(['', '\n', '\n', '\r\n', '\n\n']))
    return ''.join(out)


TOKEN_POOL = ['(', ')', '[', ']', '{', '}', ',', '.', ';', '+', '-', '*', '/',
              ':=', '=', '<', '>', 'and', 'or', 'class', 'extends', 'array',
              'new', 'nil', 'if', 'else', 'while', 'return', 'int', 'string',
              'void', 'x', '5', '"s"']
BAD_CHARS = list('$#@_~`\'&|%^:!?\\') + ['"', '\x7f', '\xe9']


def mutate_tokens(toks):
    t = list(toks)
    k = R.choice(['del', 'dup', 'swap', 'ins', 'repl', 'del2'])
    i = R.randrange(len(t))
    if k == 'del':
        del t[i]
    elif k == 'del2':
        del t[i:i + 2]
    elif k == 'dup':
        t.insert(i, t[i])
    elif k == 'swap' and i + 1 < len(t):
        t[i], t[i + 1] = t[i + 1], t[i]
    elif k == 'ins':
        t.insert(i, R.choice(TOKEN_POOL))
    else:
        t[i] = R.choice(TOKEN_POOL)
    return t, 'tok-' + k


def mutate_chars(src):
    k = R.choice(['badchar', 'leadzero', 'bigint', 'badstring', 'unclosedstr',
                  'badcomment', 'unclosedcomment', 'eofcomment', 'colon'])
    i = R.randrange(len(src) + 1)
    if k == 'badchar':
        return src[:i] + R.choice(BAD_CHARS) + src[i:], 'lex-' + k
    if k == 'leadzero':
        return src[:i] + ' 0' + str(R.randint(0, 999)) + ' ' + src[i:], 'lex-' + k
    if k == 'bigint':
        return src[:i] + ' ' + str(R.choice([32768, 40000, 65536, 99999, 123456789012])) + ' ' + src[i:], 'lex-' + k
    if k == 'badstring':
        return src[:i] + ' "ab' + R.choice('1 _,9') + 'c" ' + src[i:], 'lex-' + k
    if k == 'unclosedstr':
        return src[:i] + ' "abc ' + src[i:], 'lex-' + k
    if k == 'badcomment':
        return src[:i] + R.choice([' /* a, b */ ', ' // a, b\n', ' /* "q" */ ', ' // x := y:\n']) + src[i:], 'lex-' + k
    if k == 'unclosedcomment':
        return src[:i] + ' /* never closed ', 'lex-' + k
    if k == 'eofcomment':
        return src.rstrip('\r\n') + ' // trailing', 'lex-' + k
    return src[:i] + ' : ' + src[i:], 'lex-' + k


def main():
    global R
    outdir, nvalid, nmut, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    R = random.Random(seed)
    os.makedirs(outdir + '/in', exist_ok=True)
    os.makedirs(outdir + '/out', exist_ok=True)
    exp_rows, list_rows, gen_bad = [], [], 0
    for v in range(nvalid):
        toks = program(R.choice([1, 2, 2, 3, 3, 4]))
        cases = [(render(toks), 'valid')]
        for _ in range(nmut):
            if R.random() < 0.6:
                mt, kind = mutate_tokens(toks)
                cases.append((render(mt) if mt else '', kind))
            else:
                src, kind = mutate_chars(render(toks))
                cases.append((src, kind))
        for m, (src, kind) in enumerate(cases):
            name = 'F%05d_%02d' % (v, m)
            with open('%s/in/%s.txt' % (outdir, name), 'wb') as f:
                f.write(src.encode('latin-1'))
            res = ref.judge(src)
            if kind == 'valid' and res != 'OK':
                gen_bad += 1
            exp_rows.append('%s\t%s\t%s' % (name, res, kind))
            list_rows.append('%s/in/%s.txt\t%s/out/%s.txt' % (outdir, name, outdir, name))
    open(outdir + '/expected.tsv', 'w').write('\n'.join(exp_rows) + '\n')
    open(outdir + '/list.tsv', 'w').write('\n'.join(list_rows) + '\n')
    print('generated %d files (%d valid programs); generator/ref disagreements on valid: %d'
          % (len(exp_rows), nvalid, gen_bad))


if __name__ == '__main__':
    main()
