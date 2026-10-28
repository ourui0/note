"""Small test-only interpreter for the handout's IR instruction set."""
import re

class VM:
    def __init__(self, text, inputs=()):
        self.lines=[line.split() for line in text.splitlines() if line.strip()]
        self.functions={}; self.labels={}; self.memory={}; self.next_address=4096
        self.inputs=iter(inputs); self.outputs=[]; self.steps=0
        for i,t in enumerate(self.lines):
            if t[0]=='FUNCTION':
                assert len(t)==3 and t[2]==':' and t[1] not in self.functions
                self.functions[t[1]]=i+1
            if t[0]=='LABEL':
                assert len(t)==3 and t[2]==':' and t[1] not in self.labels
                self.labels[t[1]]=i+1

    def call(self,name,args=()):
        frame={}; addresses={}; pending=[]; params=iter(args)
        def value(s):
            if s.startswith('#'): return int(s[1:])
            if s.startswith('&'): return addresses[s[1:]]
            if s.startswith('*'): return self.memory[value(s[1:])]
            return frame[s]
        def store(s,v):
            if s.startswith('*'): self.memory[value(s[1:])]=v
            else: frame[s]=v
        pc=self.functions[name]
        while pc<len(self.lines):
            self.steps+=1
            assert self.steps<2000000,'instruction limit exceeded'
            t=self.lines[pc]; pc+=1; op=t[0]
            if op=='LABEL': continue
            if op=='FUNCTION': raise AssertionError('fell through function')
            if op=='PARAM': frame[t[1]]=next(params)
            elif op=='DEC':
                size=int(t[2]); assert size>0 and size%4==0
                addresses[t[1]]=self.next_address; self.next_address+=size
            elif op=='GOTO': pc=self.labels[t[1]]
            elif op=='IF':
                assert len(t)==6 and t[4]=='GOTO'
                x,y=value(t[1]),value(t[3]); rel=t[2]
                if {'==':x==y,'!=':x!=y,'<':x<y,'>':x>y,'<=':x<=y,'>=':x>=y}[rel]: pc=self.labels[t[5]]
            elif op=='RETURN': return value(t[1])
            elif op=='ARG': pending.append(value(t[1]))
            elif op=='READ': store(t[1],next(self.inputs))
            elif op=='WRITE': self.outputs.append(value(t[1]))
            else:
                assert t[1]==':=',t
                if t[2]=='CALL':
                    result=self.call(t[3],pending[::-1]); pending=[]; store(t[0],result)
                elif len(t)==3: store(t[0],value(t[2]))
                else:
                    assert len(t)==5,t
                    x,y=value(t[2]),value(t[4])
                    if t[3]=='+': result=x+y
                    elif t[3]=='-': result=x-y
                    elif t[3]=='*': result=x*y
                    elif t[3]=='/': result=(abs(x)//abs(y))*(-1 if (x<0)!=(y<0) else 1)
                    else: raise AssertionError(t)
                    store(t[0],result)
        raise AssertionError('missing RETURN')

def run(text, inputs=()):
    vm=VM(text,inputs); result=vm.call('main'); return vm.outputs,result,vm.steps
