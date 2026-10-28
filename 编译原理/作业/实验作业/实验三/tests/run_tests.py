from pathlib import Path
import os, shlex, shutil, subprocess, sys, tempfile, re, random
from ir_vm import run

ROOT=Path(__file__).resolve().parents[1]
CODE=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'proj3_submission/Code'
cases=[]
def case(name,source,outputs=(),inputs=(),result=0):
    cases.append((name,source,list(outputs),inputs,result))

case('constant','int main(){write(1+2*3);return 0;}',[7])
case('six relations','int main(){write(1<2);write(2<=2);write(3>1);write(3>=3);write(4==4);write(4!=4);return 0;}',[1,1,1,1,1,0])
case('factorial','int fact(int n){if(n<=1)return 1;return n*fact(n-1);}int main(){write(fact(read()));return 0;}',[720],[6])
case('loop','int main(){int i=0,s=0;while(i<10){s=s+i;i=i+1;}write(s);return 0;}',[45])
case('short circuit','int main(){int x=0;0&&(x=1);1||(x=2);write(x);write(!0);write(!(1&&2));return 0;}',[0,1,0])
case('short circuit read','int main(){if(0&&read())write(99);if(1||read())write(read());return 0;}',[8],[8])
case('write value','int main(){int x;x=write(7);write(x);return 0;}',[7,0])
case('nested calls','int add(int x,int y){return x+y;}int main(){write(add(add(1,2),add(3,4)));return 0;}',[10])
case('argument order','int sub(int x,int y,int z){return x-y*10-z*100;}int main(){write(sub(1,2,3));return 0;}',[-319])
case('array','int main(){int a[4],i=0;while(i<4){a[i]=i*2;i=i+1;}write(a[3]);return 0;}',[6])
case('array parameter','int set(int a[2]){a[1]=9;return a[0];}int main(){int b[2];b[0]=4;write(set(b));write(b[1]);return 0;}',[4,9])
case('array forwarding','int f(int a[2]){a[1]=8;return 0;}int g(int b[2]){return f(b);}int main(){int c[2];g(c);write(c[1]);return 0;}',[8])
case('multi-dimensional','int main(){int a[2][3][4];a[1][2][3]=17;a[0][1][2]=9;write(a[1][2][3]+a[0][1][2]);return 0;}',[26])
case('array alias','int f(int a[2],int b[2]){a[0]=5;return b[0];}int main(){int x[2];write(f(x,x));return 0;}',[5])
case('subarray argument','int f(int a[3]){a[2]=11;return 0;}int main(){int b[2][3];f(b[1]);write(b[1][2]);return 0;}',[11])
case('boolean array index','int main(){int a[2];a[1<2]=4;write(a[1]);return 0;}',[4])
case('negative division','int main(){write(-7/3);write(7/-3);return 0;}',[-2,-2])
case('name collisions','int main(){int t1=3,v1=4,label1=5;write(t1+v1+label1);return 0;}',[12])
case('assignment snapshot','int main(){int x=1;write(x+(x=2));return 0;}',[3])
case('arguments snapshot','int f(int a,int b){return a*10+b;}int main(){int x=1;write(f(x,x=2));return 0;}',[12])
case('lvalue snapshot','int main(){int a[3],i=0;a[i]=(i=2);write(a[0]);return 0;}',[2])
case('recursive array','int sum(int a[4],int n){if(n==0)return 0;return a[n-1]+sum(a,n-1);}int main(){int b[4];b[0]=1;b[1]=2;b[2]=3;b[3]=4;write(sum(b,4));return 0;}',[10])
case('dangling else','int main(){if(1)if(0)write(1);else write(2);return 0;}',[2])
case('parentheses','int main(){int a[2],x=1;(a)[0]=3;(x)=4;write((a)[0]+x);return 0;}',[7])
case('array copy','int main(){int a[2],b[3];b[0]=6;b[1]=8;a=b;write(a[0]+a[1]);return 0;}',[14])
case('repeated arrays','int f(int p){int a[2];a[0]=p;if(p==0)return 0;return a[0]+f(p-1);}int main(){write(f(4));return 0;}',[10])
case('relation snapshot','int main(){int x=1;write(x==(x=2));return 0;}',[0])
case('assignment chain','int main(){int a,b,c;a=b=c=7;write(a+b+c);return 0;}',[21])

from pypdf import PdfReader
text='\n'.join(p.extract_text() for p in PdfReader(ROOT/'实验三——中间代码生成.pdf').pages)
text=re.sub(r'(?m)^\d{2}\s*$','',text)
official=[]
for number,block in re.findall(r'样例(\d+)\s*：\s*输入\s*：(.*?)输出\s*：',text,re.S):
    lines=re.findall(r'^[ \t]*(\d+)[ \t]+([^\n]*)',block,re.M)
    source=['']*max(int(n) for n,_ in lines)
    for n,line in lines: source[int(n)-1]=line.strip()
    official.append('\n'.join(source))
assert len(official)==4,len(official)
for n in (-5,0,7):case(f'official sign {n}',official[0],[(n>0)-(n<0)],[n])
for n,f in ((0,1),(1,1),(5,120)):case(f'official factorial {n}',official[1],[f],[n])
case('official optional 3.2',official[3],[1,3])

# Independent native-C comparisons use only defined, sequenced C expressions.
native_cases=[]
rng=random.Random(20261014)
for i in range(16):
    a,b,c=[rng.randrange(-15,16) for _ in range(3)]
    native_cases.append((f'native scalar {i}',f'int main(){{int a={a},b={b},c={c},i=0,s=0;while(i<7){{if((a+i>b)&&c!=0)s=s+a*i;else s=s-b;i=i+1;}}write(s);write((a+b)*(c-2));return 0;}}'))
for i in range(8):
    rows,cols=rng.randrange(2,5),rng.randrange(2,6)
    native_cases.append((f'native matrix {i}',f'int main(){{int a[{rows}][{cols}],i=0,j=0,s=0;while(i<{rows}){{j=0;while(j<{cols}){{a[i][j]=i*10+j;s=s+a[i][j];j=j+1;}}i=i+1;}}write(s);write(a[{rows-1}][{cols-1}]);return 0;}}'))

with tempfile.TemporaryDirectory(prefix='lab3-tests-') as folder:
    work=Path(folder)
    for p in CODE.iterdir():
        if p.suffix in ('.c','.h','.l','.y'): shutil.copy2(p,work/p.name)
    for command in [['flex','-o','lex.yy.c','lexer.l'],['bison','-d','-o','syntax.tab.c','parser.y']]:
        p=subprocess.run(command,cwd=work,capture_output=True,text=True); assert p.returncode==0,p.stderr
    sources=[str(p.name) for p in work.glob('*.c') if p.name!='lex.yy.c']
    p=subprocess.run(['cc','-std=c99','-Wall','-Wextra','-pedantic',*shlex.split(os.getenv('LAB3_CFLAGS','')),*sources,'-o','parser'],cwd=work,capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    if p.stderr: print(p.stderr)
    failures=0
    native_header='#include <stdio.h>\nint read(void){int x;scanf("%d",&x);return x;}\nint write(int x){printf("%d\\n",x);return 0;}\n'
    for name,source in native_cases:
        (work/'native.c').write_text(native_header+source)
        subprocess.run(['cc','-std=c99','native.c','-o','native'],cwd=work,check=True,capture_output=True)
        native=subprocess.run([str(work/'native')],capture_output=True,text=True,check=True)
        case(name,source,[int(x) for x in native.stdout.split()])
    for name,source,expected,inputs,result in cases:
        (work/'in.cmm').write_text(source); (work/'out.ir').unlink(missing_ok=True)
        p=subprocess.run([str(work/'parser'),str(work/'in.cmm'),str(work/'out.ir')],capture_output=True,text=True,timeout=10)
        try:
            assert p.returncode==0 and not p.stdout and not p.stderr,(p.returncode,p.stdout,p.stderr)
            got,ret,steps=run((work/'out.ir').read_text(),inputs)
            assert got==expected and ret==result,(got,ret,expected,result)
            print('PASS',name,steps,'instructions')
        except Exception as e:
            failures+=1; print('FAIL',name,repr(e))
    (work/'in.cmm').write_text(official[2])
    p=subprocess.run([str(work/'parser'),str(work/'in.cmm'),str(work/'out.ir')],capture_output=True,text=True)
    if p.returncode!=0 or p.stdout.strip()!='Cannot translate: Code contains variables or parameters of structure type.':
        failures+=1; print('FAIL unselected 3.1',p.stdout)
    original='int main(){return 0;}\n'
    (work/'alias.cmm').write_text(original)
    (work/'hard.cmm').hardlink_to(work/'alias.cmm')
    (work/'soft.cmm').symlink_to(work/'alias.cmm')
    for alias in [str(work)+'/./alias.cmm',str(work/'hard.cmm'),str(work/'soft.cmm')]:
        p=subprocess.run([str(work/'parser'),str(work/'alias.cmm'),alias],capture_output=True,text=True)
        if p.returncode==0 or (work/'alias.cmm').read_text()!=original:
            failures+=1;print('FAIL source alias protection',alias)
        (work/'alias.cmm').write_text(original)
    print(f'{len(cases)+4-failures}/{len(cases)+4} passed')
    sys.exit(bool(failures))
