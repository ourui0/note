"""Build a clean copy and check observable diagnostics, streams and exit status."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import sys
import os
import shlex

ROOT = Path(__file__).resolve().parents[1]
CODE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'proj2_submission/Code'
cases = []
def case(name, source, expected=()):
    cases.append((name, source, [(str(k), n) for k, n in expected]))

case('valid', 'int main(){return 0;}')
case('empty', '')
case('undefined variable', 'int main(){\nint i=0;\nj=i+1;\n}', [(1,3)])
case('undefined function', 'int main(){\nf(1);\n}', [(2,2)])
case('duplicate variable', 'int a;\nint a;', [(3,2)])
case('duplicate function', 'int f(){return 0;}\nint f(){return 1;}', [(4,2)])
case('assignment', 'int main(){int a;\na=1.2;}', [(5,2)])
case('left value', 'int main(){int a;\n10=a;}', [(6,2)])
case('operands', 'int main(){float a;\n10+a;}', [(7,2)])
case('return', 'int main(){\nreturn 1.2;}', [(8,2)])
case('arguments', 'int f(int p){return p;}\nint main(){f(1,2);}', [(9,2)])
case('non-array', 'int main(){int a;\na[0];}', [(10,2)])
case('non-function', 'int main(){int a;\na(0);}', [(11,2)])
case('index', 'int main(){int a[10];\na[1.5]=0;}', [(12,2)])
case('non-struct', 'int main(){int a;\na.x;}', [(13,2)])
case('missing field', 'struct A{int x;};\nint main(){struct A a;\na.y;}', [(14,3)])
case('duplicate field', 'struct A{int x;\nfloat x;};', [(15,2)])
case('initialized field', 'struct A{\nint x=0;};', [(15,2)])
case('duplicate struct', 'struct A{int x;};\nstruct A{float y;};', [(16,2)])
case('undefined struct', 'int main(){\nstruct A a;}', [(17,2)])
case('tag-variable', 'struct A{int x;};\nint A;', [(3,2)])
case('variable-tag', 'int A;\nstruct A{int x;};', [(16,2)])
case('recursive', 'int f(int p){if(p) return f(p-1); return 0;}')
case('forward call', 'int f(){return g();}\nint g(){return 0;}', [(2,1)])
case('cascade', 'int main(){\nreturn missing+1.5;}', [(1,2)])
case('multiple', 'int main(){int a;\nx=1;\na=2.0;\na[0];\nreturn 0;}', [(1,2),(5,3),(10,4)])
case('float condition', 'int main(){\nif(1.5) return 0;}', [(7,2)])
case('float logical', 'int main(){\n!1.5;}', [(7,2)])
case('array dimensions', 'int main(){int a[2][3],b[4];\na=b;}', [(5,2)])
case('array size ignored', 'int main(){int a[2][3],b[4][5]; a=b; a[1][2]=0; return 0;}')
case('struct equivalence', 'struct A{int x;float y;}; struct B{int p;float q;}; int main(){struct A a;struct B b;a=b;return a.x;}')
case('struct order', 'struct A{int x;float y;}; struct B{float p;int q;};\nint main(){struct A a;struct B b;a=b;}', [(5,2)])
case('anonymous', 'int main(){struct {int x;} a; struct {int z;} b;a=b;return a.x;}')
case('nested structures', 'struct A{struct {float x;} v[2];}; struct B{struct {float y;} w[7];}; int main(){struct A a;struct B b;a=b;return 0;}')
case('struct call', 'struct A{int x;};struct B{int y;};int f(struct A p){return p.x;}int main(){struct B b;return f(b);}')
case('no scopes', 'int f(){int a;return 0;}\nint main(){int a;return 0;}', [(3,2)])
case('no declarations', 'int f(int p);\nint main(){return 0;}', [('B',1)])
case('two declarations', 'int f(int p);\nint f(float q);\nint main(){return 0;}', [('B',1),('B',2)])
case('comments', '// hi\nint main(){/* multi\nline */return 0;}')
case('unclosed comment', 'int main(){return 0;}\n/*', [('A',2)])
case('no octal', 'int main(){\nint a=0123;}', [('B',2)])
case('no hex', 'int main(){\nint a=0x3f;}', [('B',2)])
case('no exponent', 'int main(){\nfloat a=1.2e3;}', [('B',2)])
case('no exponent trailing dot', 'int main(){\nfloat a=43.e-4;}', [('B',2)])
case('nested wrong', 'struct A{struct {float x;int y;} v[2];};struct B{struct {int p;float q;} w[2];};\nint main(){struct A a;struct B b;a=b;}', [(5,2)])
case('struct count', 'struct A{int x;float y;};struct B{int p;};\nint main(){struct A a;struct B b;a=b;}', [(5,2)])
case('field names retained', 'struct A{int x;};struct B{int y;};int main(){struct A a;struct B b;a=b;\na.y;}', [(14,2)])
case('struct return', 'struct A{int x;};struct B{int y;};struct A f(struct B p){return p;}int main(){return 0;}')
case('wrong struct return', 'struct A{int x;};struct B{float y;};\nstruct A f(struct B p){return p;}', [(8,2)])
case('wrong struct argument', 'struct A{int x;};struct B{float y;};int f(struct A p){return p.x;}\nint main(){struct B b;return f(b);}', [(9,2)])
case('array arguments', 'int f(int p[2][3]){return p[1][1];}int main(){int a[4][5];return f(a);}')
case('array argument mismatch', 'int f(int p[2][3]){return p[1][1];}\nint main(){int a[4];return f(a);}', [(9,2)])
case('parameter duplicate', 'int f(int p){return p;}\nint g(int p){return p;}', [(3,2)])
case('nested duplicate', 'int main(){int a;\n{int a;}return 0;}', [(3,2)])
case('global visibility', 'int f(int p){int v;return p;}int main(){v=p;return 0;}')
case('left binary', 'int main(){int a;\n(a+1)=2;}', [(6,2)])
case('left parentheses', 'int main(){int a;(a)=2;return a;}')
case('left function', 'int f(){return 0;}\nint main(){f()=1;}', [(6,2)])
case('all statements', 'int main(){int a=0;float b=1.0;while(a<5){a=a+1;}if(a==5&&!(a==0))a=1;else a=2;b=-b/2.0;return a;}')
case('array arithmetic', 'int main(){int a[2];\na+a;}', [(7,2)])
case('struct arithmetic', 'int main(){struct {int x;} a;\na+a;}', [(7,2)])
case('extra index', 'int main(){int a[2];\na[0][0];}', [(10,2)])
case('empty struct', 'struct A{};struct B{};int main(){struct A a;struct B b;a=b;return 0;}')

# Read numbered source lines directly from the official handout, preserving its line numbers.
try:
    from pypdf import PdfReader
    handout = '\n'.join(p.extract_text() for p in PdfReader(ROOT/'实验二_C--语义分析.pdf').pages)
    handout = re.sub(r'(?m)^\d{2}\s*$', '', handout)
    examples = re.findall(r'样例(\d+)\s*[：:]\s*输入\s*[：:](.*?)输出\s*[：:]', handout, re.S)
    official_count = 0
    for number, block in examples:
        # Empty numbered lines need a line-boundary-safe match.
        numbered = re.findall(r'^[ \t]*(\d+)[ \t]+([^\n]*)',block,re.M)
        if not numbered: continue
        source_lines = [''] * max(int(n) for n,_ in numbered)
        for n, line in numbered: source_lines[int(n)-1] = line.strip()
        source = '\n'.join(source_lines)
        official_count += 1
        expected = ([(int(number), [4,4,4,6,4,4,4,4,8,4,4,4,9,9,4,6,3][int(number)-1])]
                    if official_count<=17 else
                    [[('B',1)],[('B',6),('B',8)],[(3,9)],[(3,9),(3,10)],[],[(5,16)]][official_count-18])
        case(f'official {official_count}', source, expected)
    assert official_count == 23, official_count
except ImportError:
    print('pypdf unavailable: official PDF examples skipped')

with tempfile.TemporaryDirectory(prefix='lab2-test-') as folder:
    work = Path(folder)
    for p in CODE.iterdir():
        if p.suffix in ('.c','.h','.l','.y'): shutil.copy2(p, work/p.name)
    commands = [['flex','-o','lex.yy.c','lexer.l'], ['bison','-d','-o','syntax.tab.c','parser.y'],
                ['cc','-std=c99','-Wall','-Wextra','-pedantic',*shlex.split(os.environ.get('LAB2_CFLAGS','')),'parser.c','syntax.tab.c', *(['semantic.c'] if (work/'semantic.c').exists() else []), '-o','parser']]
    for command in commands:
        result = subprocess.run(command, cwd=work, capture_output=True, text=True)
        if result.returncode: raise RuntimeError(result.stderr)
        if result.stderr: print(result.stderr.strip())
    failed = 0
    for name, source, expected in cases:
        path = work/'input.cmm'; path.write_text(source)
        try:
            run = subprocess.run([str(work/'parser'),str(path)], capture_output=True, text=True, timeout=5)
            got = [(k,int(n)) for k,n in re.findall(r'Error type (\w+) at Line (\d+):',run.stdout)]
            good = run.returncode == 0 and not run.stderr and got == expected and (bool(expected) or not run.stdout)
        except subprocess.TimeoutExpired:
            good = False; got = 'TIMEOUT'
        if not good:
            failed += 1; print(f'FAIL {name}: expected {expected}, got {got}')
    print(f'{len(cases)-failed}/{len(cases)} passed; {failed} failed')
    sys.exit(bool(failed))
