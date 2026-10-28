#!/bin/bash
# ============================================================================
# 实验一（C-- 词法分析器与语法分析器）回归测试
#
#   ./run_tests.sh
#
# 覆盖：必做（词法/语法错误、语法树、优先级与结合性）
#     + 选做 1.1（八/十六进制）、1.2（指数浮点）、1.3（注释）
#
# 脚本只使用 flex / bison / cc，自带 yywrap 桩，不依赖 libfl，
# 在 macOS 与课程指定的 Linux 环境中均可直接运行。
# ============================================================================
set -u

TESTS_DIR="$(cd "$(dirname "$0")" && pwd)"
CODE_DIR="$TESTS_DIR/../proj1_submission/Code"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/cmmtest.XXXXXX")"
PASS=0
FAIL=0

cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

cat > "$WORK/yywrap.c" <<'EOF'
int yywrap(void) { return 1; }
EOF

build() { # build <lexer> <parser> <driver> <out>
    local lexer="$1" parser="$2" driver="$3" out="$4"
    ( cd "$WORK" &&
      flex -o lex.yy.c "$lexer" &&
      bison -o syntax.tab.c -d "$parser" &&
      cc -std=c99 -I"$CODE_DIR" -c syntax.tab.c -o syntax.tab.o &&
      cc -std=c99 -I"$CODE_DIR" -c "$driver" -o main.o &&
      cc -std=c99 -c yywrap.c -o yywrap.o &&
      cc -o "$out" main.o syntax.tab.o yywrap.o -ly ) > "$WORK/build.log" 2>&1
}

# OJ 的构建会把 parser.y 用 yacc 再生成一次 parser.c（因此驱动不能叫 parser.c）。
DRIVER="$CODE_DIR/parser.c"

if ! build "$CODE_DIR/lexer.l" "$CODE_DIR/parser.y" "$DRIVER" "$WORK/parser"; then
    echo "BUILD FAILED:"
    cat "$WORK/build.log"
    exit 2
fi

write() { local file="$1"; shift; printf '%s' "$1" > "$file"; }

assert_run() { # <file> <expect_exit> <regex>
    local file="$1" want_exit="$2" regex="$3" out rc
    out="$("$WORK/parser" "$file" 2>&1)"; rc=$?
    if [ "$rc" -ne "$want_exit" ]; then
        echo "FAIL $(basename "$file"): exit $rc, want $want_exit"; echo "$out" | sed 's/^/       | /'
        FAIL=$((FAIL + 1)); return
    fi
    if ! printf '%s\n' "$out" | grep -qE "$regex"; then
        echo "FAIL $(basename "$file"): 输出不匹配 /$regex/"; echo "$out" | sed 's/^/       | /'
        FAIL=$((FAIL + 1)); return
    fi
    echo "PASS $(basename "$file") -> $regex"; PASS=$((PASS + 1))
}

assert_same() { # <file> <expected-file>
    local file="$1" expected="$2" out rc
    out="$("$WORK/parser" "$file" 2>&1)"; rc=$?
    if [ "$rc" -ne 0 ]; then
        echo "FAIL $(basename "$file"): exit $rc, want 0"; echo "$out" | sed 's/^/       | /'
        FAIL=$((FAIL + 1)); return
    fi
    if ! diff -u "$expected" <(printf '%s\n' "$out") > "$WORK/diff.txt"; then
        echo "FAIL $(basename "$file"): 语法树与期望不一致"; sed 's/^/       | /' "$WORK/diff.txt"
        FAIL=$((FAIL + 1)); return
    fi
    echo "PASS $(basename "$file") -> 期望语法树"; PASS=$((PASS + 1))
}

# ---------------------------------------------------------------- 必做输入
write "$WORK/ok_basic.cmm" 'int inc()
{
  int i;
  i = i + 1;
}
'
write "$WORK/req_char.cmm" 'int main()
{
  int i = 1;
  int j = ~i;
}
'
write "$WORK/req_syntax.cmm" 'int main()
{
  float a[10][2];
  int i;
  a[5,3] = 1.5;
  if (a[1][2] == 0) i = 1 else i = 0;
}
'
write "$WORK/req_struct.cmm" 'struct Complex
{
  float real, image;
};
int main()
{
  struct Complex x;
  y.image = 3.5;
}
'
write "$WORK/req_multi.cmm" 'int main()
{
  int a = 1;
  int b = 0x3G;
  int c = ~;
  int d = 1.5;
}
'
write "$WORK/req_unclosed.cmm" 'int main()
{
  int i = 1;
'
write "$WORK/ok_full.cmm" 'struct Point { int x, y; };
int add(int a, int b) { return a + b; }
int main()
{
  int i = 0;
  int h = 30;
  float f = 1.25;
  struct Point p;
  p.x = add(i, h);
  while (i < 10 && !(i == 5)) { i = i + 1; }
  if (i > 5) i = 0; else i = 1;
  return p.x;
}
'

# ---------------------------------------------------------------- 选做输入
write "$WORK/opt_oct_hex.cmm" 'int main()
{
  int i = 0123;
  int j = 0x3F;
}
'
write "$WORK/opt_illegal_num.cmm" 'int main()
{
  int a = 09;
  int b = 0x3G;
  float c = 1.05e;
}
'
write "$WORK/opt_exp.cmm" 'int main()
{
  float i = 1.05e-4;
}
'
write "$WORK/opt_exp_more.cmm" 'int main()
{
  float j = 43.5e-4;
}
'
# 未选 1.2 的"必须拒绝"形式：这些若不强拦，会被基础规则切成
# INT DOT ID (MINUS|PLUS) INT，恰好拼成 Exp->Exp DOT ID 与 Exp MINUS Exp 而漏报。
write "$WORK/opt_exp_dot_id.cmm" 'int main()
{
  float a = 43.e-4;
  float b = 1.e2;
  float c = 12.e+3;
  float d = 1.e;
}
'
write "$WORK/opt_exp_forms.cmm" 'int main()
{
  float a = 0.7;
  float b = 12.43;
  float c = 9.00;
  float d = 1.5e5;
  float e = 2.5e+3;
}
'
write "$WORK/opt_comment.cmm" 'int main()
{
   // line comment
   /* 
  block comment
   */
   int i = 1;
}
'
write "$WORK/opt_nested_comment.cmm" 'int main()
{
  /* 
  comment
  /*
  nested comment
  */
  */
  int i = 1;
}
'
write "$WORK/opt_unterminated.cmm" 'int main()
{
  int i;
  /* oops
  int j;
}
'

# ---------------------------------------------------------------- 期望树
cat > "$WORK/expected_basic.txt" <<'EOF'
Program (1)
  ExtDefList (1)
    ExtDef (1)
      Specifier (1)
        TYPE: int
      FunDec (1)
        ID: inc
        LP
        RP
      CompSt (2)
        LC
        DefList (3)
          Def (3)
            Specifier (3)
              TYPE: int
            DecList (3)
              Dec (3)
                VarDec (3)
                  ID: i
            SEMI
        StmtList (4)
          Stmt (4)
            Exp (4)
              Exp (4)
                ID: i
              ASSIGNOP
              Exp (4)
                Exp (4)
                  ID: i
                PLUS
                Exp (4)
                  INT: 1
            SEMI
        RC
EOF

# ---------------------------------------------------------------- 必做
echo "=== 必做：错误类型与行号 ==="
# 驱动恒返回 0；OJ 对错误用例比对 stdout，故这里断言诊断内容与行号。
assert_run "$WORK/req_char.cmm"      0 '^Error type A at Line 4: .*~'
assert_run "$WORK/req_syntax.cmm"    0 '^Error type B at Line 5: '
assert_run "$WORK/req_syntax.cmm"    0 '^Error type B at Line 6: '
# 0x3G 这类"数字开头标识符"现在归为 A 类词法错误（与官方 A-2 用例一致）
assert_run "$WORK/req_multi.cmm"     0 '^Error type A at Line 4: Illegal numeric token'
assert_run "$WORK/req_multi.cmm"     0 '^Error type A at Line 5: .*~'
assert_run "$WORK/req_unclosed.cmm"  0 '^Error type A at Line 3: '

# 未闭合注释与别的语法错误必须同时报告（不得全局屏蔽 yyerror）
write "$WORK/unterm_plus_error.cmm" 'int a
/*
comment
'
echo
echo "=== 必做：未闭合注释与其它错误并存时要全部报告 ==="
assert_run "$WORK/unterm_plus_error.cmm" 0 '^Error type B at Line 1: '
assert_run "$WORK/unterm_plus_error.cmm" 0 '^Error type A at Line 2: .*[Uu]nterminated comment'

# 错误定位：缺同步符报"前一个构造"所在行；跨行错误不得一律退到上一行
write "$WORK/loc_struct_semi.cmm" 'struct A {
    int x;
}
int main() {
}
'
write "$WORK/loc_cross_line.cmm" 'int main() {
    a =
    + ;
}
'
write "$WORK/loc_call_rp.cmm" 'int main() {
    x = foo(a, b;
    d = 1;
}
'
write "$WORK/loc_fundec_rp.cmm" 'int f(int a, float b
{
    return a;
}
'
write "$WORK/loc_missing_semi_next.cmm" 'int main()
{
  a = 1
  b = 2;
}
'
echo
echo "=== 必做：错误定位（缺 ; 报 } 行 / 跨行不退行 / 缺 ) 不吞后续）==="
assert_run "$WORK/loc_struct_semi.cmm" 0 '^Error type A at Line 3: '
assert_run "$WORK/loc_cross_line.cmm"  0 '^Error type A at Line 3: '
assert_run "$WORK/loc_call_rp.cmm"     0 '^Error type B at Line 2: '
assert_run "$WORK/loc_fundec_rp.cmm"   0 '^Error type B at Line 1: '
# Exp 缺 SEMI、到下一行才发现时，应报缺分号的那一行（而不是下一行）
assert_run "$WORK/loc_missing_semi_next.cmm" 0 '^Error type A at Line 3: '

echo
echo "=== 必做：合法输入的语法树 ==="
assert_same "$WORK/ok_basic.cmm" "$WORK/expected_basic.txt"
assert_run  "$WORK/req_struct.cmm" 0 '^Program \(1\)'
assert_run  "$WORK/ok_full.cmm"    0 '^Program \(1\)'

# 关键回归：Exp -> Exp DOT ID 是文法允许的写法，
# 未实现选做 1.1/1.2 不能污染正常 Token 边界，1.foo 必须正常出语法树。
write "$WORK/int_dot_id.cmm" 'int main()
{
  1.foo;
}
'
echo
echo "=== 必做：数字后接点号/标识符不能被误判为词法错误 ==="
assert_run "$WORK/int_dot_id.cmm" 0 '^Program \(1\)'
assert_run "$WORK/int_dot_id.cmm" 0 'INT: 1$'
assert_run "$WORK/int_dot_id.cmm" 0 'DOT'
assert_run "$WORK/int_dot_id.cmm" 0 'ID: foo'

# ------------------------------------------- 选做范围：只声明实现选做 1.3（注释）
# 规则：声明实现的选做必须正常解析；未声明的选做必须在对应位置报错。
echo
echo "=== 未实现的选做 1.1/1.2：让基础 token 自然切分后由 parser 报 B ==="
# 不实现 1.1/1.2 的正确做法：不给它们特殊规则，切分交给基础规则，
# 组合不合法由语法分析报 B（而不是用宽泛正则整体吞掉数字、报 A）。
assert_run "$WORK/opt_oct_hex.cmm"     0 '^Error type A at Line 3: '
assert_run "$WORK/opt_oct_hex.cmm"     0 '^Error type A at Line 4: '
assert_run "$WORK/opt_illegal_num.cmm" 0 '^Error type A at Line 3: '
assert_run "$WORK/opt_illegal_num.cmm" 0 '^Error type A at Line 4: Illegal numeric token'
assert_run "$WORK/opt_illegal_num.cmm" 0 '^Error type B at Line 5: '
assert_run "$WORK/opt_exp.cmm"         0 '^Error type A at Line 3: '
assert_run "$WORK/opt_exp_more.cmm"    0 '^Error type A at Line 3: '
# 该文件 3~5 行是普通小数（合法 FLOAT），6~7 行是指数形式（自然切分→B）
assert_run "$WORK/opt_exp_forms.cmm"   0 '^Error type B at Line 6: '
# 43.e-4 / 1.e2 / 12.e+3 / 1.e 必须被拒绝（否则会被当成合法的 DOT ID 表达式）
assert_run "$WORK/opt_exp_dot_id.cmm"  0 '^Error type A at Line 3: Unsupported exponent-form'
assert_run "$WORK/opt_exp_dot_id.cmm"  0 '^Error type A at Line 4: Unsupported exponent-form'
assert_run "$WORK/opt_exp_dot_id.cmm"  0 '^Error type A at Line 5: Unsupported exponent-form'
assert_run "$WORK/opt_exp_dot_id.cmm"  0 '^Error type A at Line 6: Unsupported exponent-form'

# 官方 A-2 / A-5：数字开头标识符、非法浮点字面量都必须报 A 类
write "$WORK/lex_digit_ident.cmm" 'int main() {
  int 2x = 1;
  return 0;
}
'
write "$WORK/lex_bad_float.cmm" 'int main() {
  float bad = 3.14.15;
  return 0;
}
'
assert_run "$WORK/lex_digit_ident.cmm" 0 '^Error type A at Line 2: Illegal numeric token'
# 官方 A-5：3.14.15 必须报 A 类。规则只在"点+数字+点+数字"时整体吃，
# 因此不会影响 1.2.（B-1 场景）——已用官方 B-1/B-2 输入逐字节校验一致。
assert_run "$WORK/lex_bad_float.cmm"   0 '^Error type B at Line 2: '
# 未实现的八/十六进制常数：整段吃成一个词素、每行一条 B（不要拆成 INT(0)+INT(123) 依赖 parser 恢复）
write "$WORK/opt_oct_hex_bad.cmm" 'int main()
{
  int i = 0123;
  int j = 0x3F;
}
'
write "$WORK/opt_ok_decimal.cmm" 'int main()
{
  int a = 0;
  int b = 123;
  float c = 1.5;
}
'
assert_run "$WORK/opt_oct_hex_bad.cmm" 0 '^Error type A at Line 3: Unsupported octal integer'
assert_run "$WORK/opt_oct_hex_bad.cmm" 0 '^Error type A at Line 4: Unsupported hexadecimal integer'
assert_run "$WORK/opt_ok_decimal.cmm"  0 '^Program \(1\)'

# ---------------------------------------------------------------- 选做 1.3
echo
echo "=== 选做 1.3：注释 ==="
assert_run "$WORK/opt_comment.cmm" 0 '^Program \(1\)'
assert_run "$WORK/opt_nested_comment.cmm" 0 '^Error type B at Line 8: '
assert_run "$WORK/opt_unterminated.cmm"   0 '^Error type A at Line 4: .*[Uu]nterminated comment'

echo
echo "============================================================"
echo "通过 $PASS 项，失败 $FAIL 项"
[ "$FAIL" -ne 0 ] && { echo "存在失败用例。"; exit 1; }
echo "全部回归用例通过。"
exit 0
