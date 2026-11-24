#!/usr/bin/env python3
"""Hand-written ex2 tests (expected values set by hand from the ex1/ex2 specs).

Usage: tests.py OUTDIR      -> OUTDIR/input/TEST_*.txt + OUTDIR/expected_output/*_Expected_Output.txt
Categories:
  A valid declarations      B valid statements      C valid expressions
  D valid lexical corners   E syntax err: decls     F syntax err: statements
  G syntax err: exprs       H lexical errors        I error line numbers
  J first error wins        K stress / performance
Tests whose name contains "EOF" depend on the line reported for a syntax error
at end of input (we use the line the lexer is on at EOF, like the skeleton).
"""
import os, sys

T = []          # (name, expected, source)


def add(name, exp, src):
    T.append((name, exp, src))


def fn(body):
    """body goes on line 3 of: void main() / { / body / }"""
    return 'void main()\n{\n    %s\n}\n' % body


def ex(e):
    """expression e goes on line 3"""
    return fn('x := %s;' % e)


# ---------------------------------------------------------------- A: valid declarations
add('A01_Int_Var', 'OK', 'int x;\n')
add('A02_String_Init', 'OK', 'string s := "hello";\n')
add('A03_Void_Var', 'OK', 'void v;\n')
add('A04_Class_Type_Nil', 'OK', 'Foo f := nil;\n')
add('A05_Init_Expression', 'OK', 'int x := 5 + 3 * 2;\n')
add('A06_Init_New_Array', 'OK', 'IntArr a := new int[10];\n')
add('A07_Init_New_Class', 'OK', 'Node n := new Node;\n')
add('A08_Init_New_Scalar', 'OK', 'int i := new int;\n')
add('A09_Array_Typedefs', 'OK', 'array IntArr = int[];\narray StrArr = string[];\narray NodeArr = Node[];\narray VoidArr = void[];\n')
add('A10_Array_Of_Array', 'OK', 'array IntArr = int[];\narray Matrix = IntArr[];\n')
add('A11_Class_One_Field', 'OK', 'class A { int x; }\n')
add('A12_Class_Hierarchy', 'OK', '''class Shape
{
    int sides := 0;
    string name := "shape";
    int area() { return 0; }
}
class Square extends Shape
{
    int len;
    int area() { return len * len; }
    void setLen(int l) { len := l; }
}
''')
add('A13_Field_Init_New', 'OK', 'class A { IntArr a := new int[5]; B b := new B; int c := new int; }\n')
add('A14_Func_No_Params', 'OK', 'void main() { return; }\n')
add('A15_Func_Many_Params', 'OK', 'int f(int a, string b, Node c, IntArr d, void e) { return a; }\n')
add('A16_Func_Returns_Class', 'OK', 'Node make() { Node n := new Node; return n; }\n')
add('A17_Mixed_Order', 'OK', '''array IntArr = int[];
class List { int head; List tail; }
int g := 7;
void main() { List l := new List; l.head := g; }
class Pair { int a; int b; }
string name := "end";
''')
add('A18_Method_Local_Class_Vars', 'OK', 'class A { void m() { A other := new A; B b := nil; other.m(); } }\n')
add('A19_Field_Init_Call', 'OK', 'class A { int x := f(1); int y := o.m(2, 3); }\n')
add('A20_Global_Init_Method_Call', 'OK', 'int x := a.b.c(1, 2);\n')
add('A21_Class_Method_Only', 'OK', 'class A { int add(int a, int b) { return a + b; } }\n')
add('A22_Class_Extends_Unknown_Ok', 'OK', 'class B extends A { int x; }\n')
add('A23_Many_Classes_Fields_Methods', 'OK', '''class A { int x; int y := 1; void f() { x := y; } string s; }
class B extends A { A a := new A; IntArr arr := new int[3]; int g(A p, B q) { return p.x + q.y; } }
class C extends B { void h() { g(a, nil); this.a.f(); } }
''')
add('A24_Var_Of_Every_Type', 'OK', 'int a; string b; void c; Node d; IntArr e;\n')
add('A25_Init_Negative', 'OK', 'int x := -1;\n')

# ---------------------------------------------------------------- B: valid statements
add('B01_All_Statement_Forms', 'OK', '''void main()
{
    int x;
    int y := 1;
    A a := new A;
    x := y;
    a := new A;
    return;
    return x;
    if (x) { x := 1; }
    if (x) { x := 1; } else { x := 2; }
    while (x) { x := x - 1; }
    f(x);
    a.m(x);
}
''')
add('B02_If_No_Else', 'OK', fn('if (x < 10) { x := x + 1; }'))
add('B03_If_Else', 'OK', fn('if (x < 10) { x := 1; } else { x := 2; }'))
add('B04_Else_With_Nested_If', 'OK', fn('if (a) { x := 1; } else { if (b) { x := 2; } else { x := 3; } }'))
add('B05_While_Nested', 'OK', fn('while (i < n) { j := 0; while (j < n) { if (a[i] > a[j]) { t := a[i]; } j := j + 1; } i := i + 1; }'))
add('B06_Return_Forms', 'OK', 'int f() { return 1; }\nvoid g() { return; }\nint h() { return f() + 1; }\n')
add('B07_Call_Statements', 'OK', fn('f(); f(1); f(1, "s", nil); o.m(); o.a.b[1].m(x); printInt(f(g(h())));'))
add('B08_Assign_Targets', 'OK', fn('x := 1; o.f := 2; a[1] := 3; a[i][j] := 4; o.a[1].b := 5; a[f(1)] := 6; a[o.m()] := 7;'))
add('B09_Assign_New', 'OK', fn('x := new A; a := new int[n * 2]; m := new IntArr[f(3)]; s := new string; o.f := new B; a[1] := new int[2];'))
add('B10_Local_Decls', 'OK', fn('int x; int y := 1; A a := new A; IntArr arr := new int[3]; string s := "t"; A b := nil;'))
add('B11_Code_After_Return', 'OK', fn('return 1; x := 2; return;'))
add('B12_Deep_Mixed_Nesting', 'OK', fn(
    'if (a) { while (b) { if (c) { while (d) { if (e) { while (f) { if (g) { while (h) { if (i) { x := 1; } } } } } } } } }'))
add('B13_Single_Statement_Body', 'OK', 'void f() { return; }\n')
add('B14_Complex_While_Cond', 'OK', fn('while ((i < n) and (a[i] = 0 or o.ok(i))) { i := i + 1; }'))
add('B15_If_Cond_Calls', 'OK', fn('if (o.isEmpty() = 1 or f(x) > 2) { return; }'))
add('B16_This_Is_Just_An_ID', 'OK', fn('this.x := 1; super.f(); this.list.head := nil;'))
add('B17_Stmt_Starting_With_Type_ID', 'OK', fn('Node n; n := nil; Node m := n;'))
add('B18_Empty_Lines_Between_Stmts', 'OK', 'void main()\n{\n\n    x := 1;\n\n\n    y := 2;\n\n}\n')
add('B19_Else_Block_Multi', 'OK', fn('if (x) { a := 1; b := 2; } else { c := 3; d := 4; e := 5; }'))
add('B20_Method_Body_Has_All', 'OK', '''class A
{
    int v;
    int run(int n)
    {
        int i := 0;
        while (i < n) { if (i = 3) { return i; } else { v := v + i; } i := i + 1; }
        return v;
    }
}
''')

# ---------------------------------------------------------------- C: valid expressions
add('C01_Each_Binop', 'OK', fn('x := a + b; x := a - b; x := a * b; x := a / b; x := a < b; x := a > b; x := a = b; x := a and b; x := a or b;'))
add('C02_Mixed_Precedence', 'OK', ex('a + b * c - d / e < f and g = h or i > j'))
add('C03_Nested_Parens', 'OK', ex('((a + b) * (c - (d / (e))))'))
add('C04_Negative_Ints', 'OK', fn('x := -1; x := 5 - -3; x := -32767; x := f(-1, -2); x := a[-1]; x := -0;'))
add('C05_Nil_And_Strings', 'OK', fn('x := nil = y; s := "a" + "b"; f(nil, "", "abc"); x := "s" = nil;'))
add('C06_Calls_In_Exprs', 'OK', ex('f(g(1), h(i(2), j)) + o.m(k) * a.b.c(d[1])'))
add('C07_Var_Chains', 'OK', fn('x := a.b.c.d; x := a[1][2][3]; x := a.b[1].c[2].d; x := a[b[c[d]]];'))
add('C08_And_Or_Chain', 'OK', ex('a and b or c and d or e'))
add('C09_Left_Assoc_Chain', 'OK', ex('1 - 2 - 3 - 4 / 5 / 6'))
add('C10_Equality_Chain', 'OK', ex('a = b = c'))
add('C11_Compare_Chain', 'OK', ex('a < b < c > d'))
add('C12_Paren_Literals', 'OK', fn('x := (1); x := ((nil)); x := ("s"); x := (-5);'))
add('C13_Args_With_Exprs', 'OK', fn('f((1 + 2) * 3, a[i + 1], o.m(x) - 1, (nil), -4);'))
add('C14_Minus_Without_Spaces', 'OK', fn('x := 3-2; x := 3--2; x := a-1; x := a- -1;'))
add('C15_Minus_Space_Before_Int', 'OK', fn('x := - 5; y := -\n5;'))
add('C16_Method_Call_With_Index_Base', 'OK', ex('a[1].m(2) + a.b[c].d(e)'))
add('C17_Call_Arg_Is_Method_Call', 'OK', ex('f(o.m(p.n(q.r())))'))
add('C18_Exp_All_Leaf_Kinds', 'OK', ex('a + 1 + -2 + nil + "s" + f() + o.m() + a[0] + a.b + (3)'))
add('C19_Int_Bounds', 'OK', fn('x := 0; x := 32767; x := -32767; x := 1;'))
add('C20_Index_By_Call_Result', 'OK', ex('a[f(1)][o.m()][a[2]]'))

# ---------------------------------------------------------------- D: valid lexical corner cases
add('D01_Keyword_Prefixed_IDs', 'OK', 'int intx; string strings; void voidy; classA classy; int iff; int whilex; int returnn; int newa; int nilx; int andy; int orx; int elsee; int arrayy; int extendsx; Int INT; IF If;\n')
add('D02_IDs_With_Digits', 'OK', 'int a1b2c3; int Z9; int x0; int L00;\n')
add('D03_Comment_All_Allowed_Chars', 'OK', '// abc XYZ 019 ()[]{}?!+-*/.; \t end\nint x;\n/* abc XYZ 019 ()[]{}?!+-*/\nint y;\n/* multi\n\tline ? ! + - * / . ; ( ) [ ] { }\n*/\nint z;\n')
add('D04_Odd_Block_Comments', 'OK', '/**/ int a; /***/ int b; /* / * */ int c; /*/ x */ int d; /* ** // */ int e;\n')
add('D05_Comments_Between_Tokens', 'OK', 'int/*c*/x/*c*/:=/*c*/1/*c*/;\nvoid/**/f(/**/)/**/{/**/return/**/;/**/}\n')
add('D06_Comment_Ends_Before_Code', 'OK', fn('x := a * /* comment */ b; y := a / /* c */ b;'))
add('D07_Line_Comment_Then_Divide', 'OK', 'void main()\n{\n    x := a // note\n    / b;\n}\n')
add('D08_CRLF_Line_Endings', 'OK', 'void main()\r\n{\r\n    int x := 1;\r\n    // comment\r\n    x := x + 1;\r\n}\r\n')
add('D09_CR_Only_Line_Endings', 'OK', 'void main()\r{\r    int x := 1; // c\r}\r')
add('D10_Tabs_No_Trailing_Newline', 'OK', 'void\tmain()\t{\tint\tx\t:=\t1;\t}')
add('D11_Many_Blank_Lines', 'OK', '\n\n\n\nint x;\n\n\n\n\nint y;\n\n\n')
add('D12_Empty_And_Long_String', 'OK', 'string a := ""; string b := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";\n')
add('D13_Line_Comment_Last_Line_With_Newline', 'OK', 'int x; // the end\n')
add('D14_Comment_Only_Lines_Around', 'OK', '// header\n/* block */\nint x;\n// footer\n')
add('D15_No_Whitespace_At_All', 'OK', 'void f(){x:=a+b*c;if(x){return;}else{while(y){g(1,2);}}}')
add('D16_Number_Then_ID_No_Space', 'OK', fn('x := 1 + 2;'))
add('D17_Comment_Star_Slash_Inside_Line_Comment', 'OK', 'int x; // a */ b /* c\nint y;\n')
add('D18_Assign_Glued', 'OK', fn('x:=1;y:=-2;z:=x-y;'))

# ---------------------------------------------------------------- E: syntax errors in declarations
add('E01_Missing_Semicolon_Global', 'ERROR(2)', 'int x\nint y;\n')
add('E02_Init_Missing_Exp', 'ERROR(1)', 'int x := ;\n')
add('E03_ID_Only_Dec', 'ERROR(1)', 'x;\n')
add('E04_Type_Only_Dec', 'ERROR(1)', 'int;\n')
add('E05_Number_As_Name', 'ERROR(1)', 'int 5;\n')
add('E06_Typedef_With_Size', 'ERROR(1)', 'array A = int[5];\n')
add('E07_Typedef_Assign_Not_Eq', 'ERROR(1)', 'array A := int[];\n')
add('E08_Typedef_No_Name', 'ERROR(1)', 'array = int[];\n')
add('E09_Typedef_Missing_Semicolon_EOF', 'ERROR(2)', 'array A = int[]\n')
add('E10_Empty_Class', 'ERROR(1)', 'class A { }\n')
add('E11_Extends_Nothing', 'ERROR(1)', 'class A extends { int x; }\n')
add('E12_Class_No_Name', 'ERROR(1)', 'class { int x; }\n')
add('E13_Statement_In_Class', 'ERROR(4)', 'class A\n{\n    int x;\n    x := 5;\n}\n')
add('E14_Nested_Class', 'ERROR(3)', 'class A\n{\n    class B { int y; }\n}\n')
add('E15_Typedef_In_Class', 'ERROR(2)', 'class A {\n    array T = int[];\n}\n')
add('E16_Func_Without_Body', 'ERROR(1)', 'void f();\n')
add('E17_Func_Empty_Body', 'ERROR(3)', 'int f()\n{\n}\n')
add('E18_Param_Without_Type', 'ERROR(1)', 'void f(x) { return; }\n')
add('E19_Param_Default_Value', 'ERROR(1)', 'void f(int x := 1) { return; }\n')
add('E20_Params_Trailing_Comma', 'ERROR(1)', 'void f(int x,) { return; }\n')
add('E21_Params_Leading_Comma', 'ERROR(1)', 'void f(, int x) { return; }\n')
add('E22_Params_Semicolon_Sep', 'ERROR(1)', 'void f(int x; int y) { return; }\n')
add('E23_Nested_Function', 'ERROR(4)', 'void f()\n{\n    int x;\n    int g() { return 1; }\n}\n')
add('E24_Global_Assignment', 'ERROR(3)', 'int x;\n\nx := 1;\n')
add('E25_Global_Return', 'ERROR(1)', 'return 1;\n')
add('E26_Global_If', 'ERROR(1)', 'if (x) { return; }\n')
add('E27_Global_Call', 'ERROR(1)', 'f();\n')
add('E28_Extends_Two', 'ERROR(1)', 'class A extends B, C { int x; }\n')
add('E29_Class_Missing_Brace_EOF', 'ERROR(3)', 'class A {\n    int x;\n')
add('E30_Func_Missing_Name', 'ERROR(1)', 'int (int x) { return x; }\n')
add('E31_Func_Body_No_Braces', 'ERROR(1)', 'void f() return;\n')
add('E32_New_With_Parens', 'ERROR(1)', 'A a := new A();\n')
add('E33_Java_Array_Type', 'ERROR(1)', 'int[] a;\n')
add('E34_New_Array_No_Size', 'ERROR(1)', 'int x := new int[];\n')
add('E35_New_2D_Array', 'ERROR(1)', 'int x := new int[5][5];\n')
add('E36_New_Number', 'ERROR(1)', 'int x := new 5;\n')
add('E37_Multi_Var_Dec', 'ERROR(1)', 'int x, y;\n')
add('E38_Chained_Init', 'ERROR(1)', 'int x := y := 1;\n')
add('E39_Empty_File', 'ERROR(1)', '')
add('E40_Only_Comments_EOF', 'ERROR(3)', '/* nothing */\n// here\n')
add('E41_Extends_Two_Names', 'ERROR(1)', 'class A extends B C { int x; }\n')
add('E42_Keyword_As_Var_Name', 'ERROR(1)', 'int while;\n')
add('E43_Keyword_As_Class_Name', 'ERROR(1)', 'class int { int x; }\n')
add('E44_Keyword_As_Func_Name', 'ERROR(1)', 'void return() { return; }\n')
add('E45_New_In_Exp_Init', 'ERROR(1)', 'int x := 1 + new int;\n')
add('E46_Class_Field_Missing_Semicolon', 'ERROR(4)', 'class A\n{\n    int x\n}\n')
add('E47_Error_After_Valid_Decls', 'ERROR(5)', 'int a;\nint b := 2;\nclass C { int c; }\nvoid f() { return; }\nint e := 5 5;\n')
add('E48_Typedef_Paren', 'ERROR(1)', 'array A = int();\n')
add('E49_Class_Brace_Semicolon_After', 'ERROR(1)', 'class A { int x; };\n')
add('E50_Func_Semicolon_After_Body', 'ERROR(1)', 'void f() { return; };\n')

# ---------------------------------------------------------------- F: syntax errors in statements (error on line 3)
F = [
    ('F01_If_No_Parens', 'if x { return; }'),
    ('F02_If_No_Braces', 'if (x) return;'),
    ('F03_Else_No_Braces', 'if (x) { return; } else return;'),
    ('F04_Else_If', 'if (x) { return; } else if (y) { return; }'),
    ('F05_While_Empty_Body', 'while (x) { }'),
    ('F06_While_No_Braces', 'while (x) x := 1;'),
    ('F07_If_Empty_Cond', 'if () { return; }'),
    ('F08_If_Empty_Body', 'if (x) { }'),
    ('F09_Assign_To_Call', 'f() := 1;'),
    ('F10_Assign_To_Literal', '5 := x;'),
    ('F11_New_With_Parens', 'x := new A();'),
    ('F12_New_In_Binop', 'x := 1 + new int;'),
    ('F13_New_As_Statement', 'new A;'),
    ('F14_Chained_Assign', 'x := y := 1;'),
    ('F15_Plus_Assign', 'x += 1;'),
    ('F16_Increment', 'x++;'),
    ('F17_For_Loop', 'for (i) { return; }'),
    ('F18_Var_Statement', 'x;'),
    ('F19_Extra_Semicolon', 'f();;'),
    ('F20_Bare_Block', '{ x := 1; }'),
    ('F21_Return_Two_Exps', 'return x y;'),
    ('F23_Two_Decls_No_Semicolon', 'int x := 1 int y;'),
    ('F24_Else_Without_If', 'else { return; }'),
    ('F25_Else_Empty', 'if (x) { return; } else { }'),
    ('F26_While_Else', 'while (x) { return; } else { return; }'),
    ('F27_Field_Assign_Missing_Exp', 'x.f := ;'),
    ('F28_Empty_Index_Target', 'x[] := 1;'),
    ('F29_Unclosed_Index', 'x[1 := 2;'),
    ('F30_Dot_Then_Nothing', 'x := a.;'),
    ('F31_Leading_Dot', 'x := .a;'),
    ('F32_Field_Statement', 'a.b.c;'),
    ('F33_Return_Return', 'return return;'),
    ('F34_Typedef_In_Func', 'array T = int[];'),
    ('F35_Class_In_Func', 'class C { int x; }'),
    ('F38_If_Missing_Rparen', 'if (x { return; }'),
    ('F39_While_Extra_Rparen', 'while (x)) { return; }'),
    ('F41_Double_Else', 'if (x) { return; } else { return; } else { return; }'),
    ('F42_Assign_Eq_Instead', 'x = 1;'),
    ('F43_Var_Dec_Paren_Init', 'int x(5);'),
    ('F44_Call_Missing_Rparen', 'f(1, 2;'),
    ('F45_Method_Call_No_Semicolon_Then_Stmt', 'o.m() x := 1;'),
    ('F46_Return_Assign', 'return x := 1;'),
    ('F47_If_Cond_Is_Assign', 'if (x := 1) { return; }'),
    ('F48_Decl_In_If_Cond', 'if (int x) { return; }'),
    ('F49_New_Index_On_Var', 'x := new a[1].b;'),
    ('F50_Semicolon_After_If', 'if (x) { return; };'),
]
for name, body in F:
    add(name, 'ERROR(3)', fn(body))
add('F22_Missing_Semicolon_Next_Line', 'ERROR(4)', 'void main()\n{\n    x := 1\n}\n')
add('F36_Missing_Func_Brace_EOF', 'ERROR(4)', 'void main()\n{\n    return;\n')
add('F37_Extra_Closing_Brace', 'ERROR(5)', 'void main()\n{\n    return;\n}\n}\n')
add('F40_Error_On_Continuation_Line', 'ERROR(4)', 'void main()\n{\n    x :=\n    ;\n}\n')

# ---------------------------------------------------------------- G: syntax errors in expressions (line 3)
G = [
    ('G01_Unary_Minus_Var', '-x'), ('G02_Unary_Minus_Paren', '-(1)'), ('G03_Double_Unary_Minus', '- -1'),
    ('G04_Two_Operators', '1 + * 2'), ('G05_Missing_Right_Operand', '1 +'), ('G06_Missing_Left_Operand', '* 2'),
    ('G07_Unclosed_Paren', '(1 + 2'), ('G08_Extra_Rparen', '1 + 2)'), ('G09_Empty_Parens', '()'),
    ('G10_Field_Of_Call', 'a.f().g'), ('G11_Call_Of_Call', 'f()()'), ('G12_Index_Of_Paren', '(a)[1]'),
    ('G13_Field_Of_Paren', '(a).b'), ('G14_Field_Is_Number', 'a.1'), ('G15_Empty_Index', 'a[]'),
    ('G16_Args_Trailing_Comma', 'f(1,)'), ('G17_Args_Leading_Comma', 'f(,1)'), ('G18_Minus_Nil', '-nil'),
    ('G19_Two_Ints', '5 5'), ('G20_Two_Strings', '"a" "b"'), ('G21_Two_IDs', 'a b'),
    ('G22_Index_Of_Call', 'f()[0]'), ('G23_Field_Of_Plain_Call', 'f().x'), ('G24_Star_Slash_Outside_Comment', 'a*/b'),
    ('G25_Not_Operator_Word', 'not a'), ('G26_Double_Equals', 'a == b'), ('G27_Less_Equal', 'a <= b'),
    ('G28_Not_Equal', 'a <> b'), ('G29_And_And', 'a and and b'), ('G30_Method_Call_Of_Call', 'a.f(1)(2)'),
    ('G31_New_As_Arg', 'f(new int)'), ('G32_New_In_Parens', '(new A)'), ('G33_Index_After_Method_Call', 'a[1].f()[2]'),
    ('G34_Unbalanced_Nested', '1 + (2 * 3'), ('G35_Field_Of_Nil', 'nil.f'), ('G36_Method_Of_String', '"s".f()'),
    ('G37_Method_Of_Int', '5.f()'), ('G38_Minus_Field', '-a.b'), ('G39_Hex_Literal', '0x10'),
    ('G40_Exponent_Literal', '1e5'), ('G41_Decimal_Literal', '3.14'), ('G42_Keyword_In_Exp', 'a + while'),
    ('G43_Type_In_Exp', 'int + 1'), ('G44_Array_Literal', '{1, 2}'), ('G45_Minus_String', '-"s"'),
    ('G46_Paren_Exp_Then_Paren', '(a)(b)'), ('G47_Assign_In_Exp', '(y := 1)'), ('G48_Plus_Unary', '+1'),
]
for name, e in G:
    add(name, 'ERROR(3)', ex(e))

# ---------------------------------------------------------------- H: lexical errors (plain ERROR)
H = [
    ('H01_Leading_Zero', 'int x := 01;\n'),
    ('H02_Double_Zero', 'int x := 00;\n'),
    ('H03_Leading_Zero_Deep_In_Func', fn('if (a) { while (b) { x := 007; } }')),
    ('H04_Int_32768', 'int x := 32768;\n'),
    ('H05_Int_99999', 'int x := 99999;\n'),
    ('H06_Int_Huge', 'int x := 100000000000000000000;\n'),
    ('H07_Negative_32768', 'int x := -32768;\n'),
    ('H08_Int_Six_Digits', 'int x := 327670;\n'),
    ('H09_String_With_Digit', 'string s := "abc1";\n'),
    ('H10_String_With_Space', 'string s := "a b";\n'),
    ('H11_String_With_Underscore', 'string s := "a_b";\n'),
    ('H12_String_Unclosed_Midfile', 'string s := "abc;\nint y;\nint z;\n'),
    ('H13_String_Unclosed_EOF', 'string s := "abc'),
    ('H14_String_Escaped_Quote', 'string s := "a\\"b";\n'),
    ('H15_String_With_Tab', 'string s := "a\tb";\n'),
    ('H16_String_Single_Quotes', "string s := 'abc';\n"),
    ('H17_Lone_Quote_EOF', 'int x;\n"'),
    ('H18_Block_Comment_Unclosed', 'int x;\n/* never\nclosed\n'),
    ('H19_Block_Comment_Comma', '/* a, b */ int x;\n'),
    ('H20_Block_Comment_Quote', '/* say "hi" */ int x;\n'),
    ('H21_Block_Comment_Colon', '/* x: y */ int x;\n'),
    ('H22_Block_Comment_Equals', '/* a = b */ int x;\n'),
    ('H23_Block_Comment_Less', '/* a < b */ int x;\n'),
    ('H24_Block_Comment_Bad_Char_Line3', '/* fine\nfine\nnot fine # here */\nint x;\n'),
    ('H25_Line_Comment_Comma', 'int x; // a, b\n'),
    ('H26_Line_Comment_Apostrophe', "int x; // it's\n"),
    ('H27_Line_Comment_At_EOF', 'int x; // no newline'),
    ('H28_Empty_Line_Comment_At_EOF', 'int x; //'),
    ('H29_Bang_In_Code', fn('if (!x) { return; }')),
    ('H30_Question_In_Code', fn('x := a ? b;')),
    ('H31_Lone_Colon', 'x : int;\n'),
    ('H32_Colon_Space_Equals', 'int x : = 5;\n'),
    ('H33_Underscore_ID', 'int my_var;\n'),
    ('H34_Dollar', 'int $x;\n'),
    ('H35_Hash', 'int x; #include\n'),
    ('H36_At', 'int x := @;\n'),
    ('H37_Double_Ampersand', fn('if (a && b) { return; }')),
    ('H38_Double_Pipe', fn('if (a || b) { return; }')),
    ('H39_Percent', fn('x := a % b;')),
    ('H40_Backslash', 'int x; \\\n'),
    ('H41_Caret', fn('x := a ^ b;')),
    ('H42_Tilde', fn('x := ~a;')),
    ('H43_Non_ASCII_Letter', 'int café;\n'),
    ('H44_Error_First_Char', '$int x;\n'),
    ('H45_Error_Last_Char_No_Newline', 'int x;$'),
    ('H46_Backtick', 'int `x`;\n'),
    ('H47_Leading_Zero_Index', fn('a[01] := 1;')),
    ('H48_Bad_Char_In_String_Arg', fn('f("hello!");')),
    ('H49_Bad_Char_After_Valid_Comment', '/* a /* b */ int x # ;\n'),
    ('H50_Line_Comment_Then_Bad_Next_Line', 'int x; // fine\nint y := 1 #\n'),
]
for name, src in H:
    add(name, 'ERROR', src)

# ---------------------------------------------------------------- I: error line numbers
add('I01_Error_First_Token', 'ERROR(1)', ';\n')
add('I02_After_Ten_Blank_Lines', 'ERROR(11)', '\n' * 10 + 'int x := ;\n')
add('I03_After_Multiline_Comment', 'ERROR(6)', '/* line1\nline2\nline3\nline4\nline5 */\nint ;\n')
add('I04_Same_Line_As_Comment_End', 'ERROR(2)', '/* a\nb */ int ;\n')
add('I05_CRLF_Error_Line', 'ERROR(4)', 'int a;\r\nint b;\r\nint c;\r\nint ;\r\n')
add('I06_CR_Only_Error_Line', 'ERROR(3)', 'int a;\rint b;\rint ;\r')
add('I07_Mixed_Line_Endings', 'ERROR(6)', 'int a;\nint b;\r\nint c;\rint d;\n\rint ;\n')
add('I08_After_Line_Comments', 'ERROR(3)', '// c1\n// c2\nint x := ;\n')
add('I09_EOF_With_Trailing_Newline', 'ERROR(2)', 'int x := 1\n')
add('I10_EOF_Without_Trailing_Newline', 'ERROR(1)', 'int x := 1')
add('I11_EOF_With_Many_Newlines', 'ERROR(5)', 'void f() {\n    return;\n\n\n')
add('I12_Multiline_Expression', 'ERROR(5)', 'void main()\n{\n    x := 1 +\n    2 +\n    ;\n}\n')
add('I13_Deep_In_File', 'ERROR(52)', 'int g;\n' + ''.join('int v%d := %d;\n' % (k, k) for k in range(50)) + 'int bad := := 1;\n')
add('I14_Tab_Indented', 'ERROR(4)', 'void main()\n{\n\tx := 1;\n\t\ty := ;\n}\n')
add('I15_Nested_Comment_Not_Supported', 'ERROR(1)', '/* a /* b */ c */\nint x;\n')
add('I16_Error_Token_After_Long_Line', 'ERROR(2)', 'int ' + 'a' * 300 + ' := ' + ' + '.join(['1'] * 200) + ';\nint := 2;\n')
add('I17_Error_Inside_Class_Method', 'ERROR(7)', 'class A\n{\n    int x;\n    void m()\n    {\n        x := 1;\n        x := x +;\n    }\n}\n')
add('I18_Error_After_Line_Comment_Same_Line', 'ERROR(2)', 'int a; // ok\nint b := ; // comment\n')
add('I19_Error_In_Else_Branch', 'ERROR(6)', 'void main()\n{\n    if (x)\n    { x := 1; }\n    else\n    { x := ; }\n}\n')
add('I21_Comment_Closed_Early_Then_Tokens', 'ERROR(1)', '/* a /* b */ c, */\nint x;\n')
add('I20_Error_Is_EOF_After_Comment', 'ERROR(3)', 'void f() {\n    return;\n/* never closed brace */')

# ---------------------------------------------------------------- J: first error wins
add('J01_Syntax_Then_Lexical', 'ERROR(2)', 'int a;\nint b := ;\nint c;\nint d := 007;\n')
add('J02_Lexical_Then_Syntax', 'ERROR', 'int a;\nint b := 007;\nint c;\nint d := ;\n')
add('J03_Same_Line_Syntax_First', 'ERROR(1)', 'int x := ; $\n')
add('J04_Same_Line_Lexical_First', 'ERROR', 'int x := $ ;\n')
add('J05_Lexical_Where_Syntax_Would_Fail', 'ERROR', 'int x := 5 $\n')
add('J06_Valid_Then_Bad_Comment', 'ERROR', 'int x;\nvoid f() { return; }\n/* bad, comment */\n')
add('J07_Syntax_Then_Unclosed_Comment', 'ERROR(2)', 'int a;\nint ;\n/* unclosed\n')
add('J08_Incomplete_Then_EOF_Comment', 'ERROR', 'int x := 1 // c')
add('J09_Incomplete_Then_Unclosed_Comment', 'ERROR', 'int x := 1 /* unclosed')
add('J10_Complete_Then_Bad_Char', 'ERROR', 'int x;\n@')
add('J11_Syntax_Then_Bad_String', 'ERROR(1)', 'int x := ; string s := "a1";\n')
add('J12_Lexical_In_First_Line', 'ERROR', '#\nint ;\n')

# ---------------------------------------------------------------- K: stress / performance
K = []
K.append(('K01_2000_Functions', 'OK', ''.join('int f%d(int a, int b) { int c := a + b; if (c > %d) { return c; } return a * b; }\n' % (k, k % 1000) for k in range(2000))))
K.append(('K02_If_Depth_300', 'OK', fn('if (a) { ' * 300 + 'x := 1;' + ' }' * 300)))
K.append(('K03_Expression_3000_Terms', 'OK', ex(' + '.join('a%d * %d' % (k, k % 100) for k in range(3000)))))
K.append(('K04_Paren_Depth_1000', 'OK', ex('(' * 1000 + '1' + ')' * 1000)))
K.append(('K05_Field_Chain_1000', 'OK', ex('a' + ''.join('.f%d' % k for k in range(1000)))))
K.append(('K06_500_Params', 'OK', 'void f(' + ', '.join('int p%d' % k for k in range(500)) + ') { return; }\n'))
K.append(('K07_Class_1000_Fields', 'OK', 'class Big\n{\n' + ''.join('    int f%d := %d;\n' % (k, k) for k in range(1000)) + '}\n'))
K.append(('K08_Big_File_Syntax_Error_Last_Line', 'ERROR(5003)', 'void main()\n{\n' + ''.join('    x := x + %d;\n' % (k % 30000) for k in range(5000)) + '    x := ;\n}\n'))
K.append(('K09_Big_File_Lexical_Error_At_End', 'ERROR', 'void main()\n{\n' + ''.join('    x := x + %d;\n' % (k % 30000) for k in range(5000)) + '}\n$'))
K.append(('K10_Long_String', 'OK', 'string s := "' + 'ab' * 5000 + '";\n'))
K.append(('K11_Long_Comment', 'OK', '/*' + ('lorem ipsum ( ) [ ] ; .\n' * 4000) + '*/\nint x;\n'))
K.append(('K12_20000_Statements_One_Func', 'OK', 'void main()\n{\n' + '    f(1);\n' * 20000 + '}\n'))
K.append(('K13_Call_Nesting_500', 'OK', ex('f(' * 500 + '1' + ')' * 500)))
K.append(('K14_Index_Nesting_500', 'OK', ex('a[' * 500 + '1' + ']' * 500)))
K.append(('K15_While_Depth_300_Error_At_Bottom', 'ERROR(3)', fn('while (a) { ' * 300 + 'x := ;' + ' }' * 300)))
for k in K:
    add(*k)


def main():
    out = sys.argv[1]
    os.makedirs(out + '/input', exist_ok=True)
    os.makedirs(out + '/expected_output', exist_ok=True)
    names = set()
    for name, exp, src in T:
        assert name not in names, name
        names.add(name)
        base = 'TEST_' + name
        with open('%s/input/%s.txt' % (out, base), 'wb') as f:
            f.write(src.encode('utf-8'))
        with open('%s/expected_output/%s_Expected_Output.txt' % (out, base), 'wb') as f:
            f.write(exp.encode('ascii'))
    print('wrote %d tests' % len(T))


if __name__ == '__main__':
    main()
