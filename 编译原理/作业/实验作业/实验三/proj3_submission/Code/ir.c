/* Lab 3: linear three-address IR; optional 3.2 only. */
#include "ir.h"
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

typedef struct Allocation { void *p; struct Allocation *next; } Allocation;
typedef struct Shape { long size; struct Shape *element; } Shape;
typedef struct Variable { const char *source,*name; Shape *type; int reference; struct Variable *next; } Variable;
typedef struct Line { char *text; struct Line *next; } Line;
typedef struct { const char *operand; Shape *type; } Value;
typedef struct Argument { const char *value; struct Argument *next; } Argument;
static Allocation *allocations;
static Variable *variables;
static Line *head,*tail;
static unsigned temp_id,var_id,label_id;
static Shape scalar={4,NULL};

static void *alloc(size_t size) {
    Allocation *a=checked_malloc(sizeof(*a)); a->p=checked_malloc(size);
    memset(a->p,0,size); a->next=allocations; allocations=a; return a->p;
}
static char *format(const char *fmt, ...) {
    va_list ap,copy; int size; char *s;
    va_start(ap,fmt); va_copy(copy,ap); size=vsnprintf(NULL,0,fmt,copy); va_end(copy);
    s=alloc((size_t)size+1); vsnprintf(s,(size_t)size+1,fmt,ap); va_end(ap); return s;
}
static void emit(const char *fmt, ...) {
    va_list ap,copy; int size; Line *line=alloc(sizeof(*line));
    va_start(ap,fmt); va_copy(copy,ap); size=vsnprintf(NULL,0,fmt,copy); va_end(copy);
    line->text=alloc((size_t)size+1); vsnprintf(line->text,(size_t)size+1,fmt,ap); va_end(ap);
    if(tail) tail->next=line; else head=line; tail=line;
}
static int named(Node *n,const char *name) { return n && !strcmp(n->name,name); }
static Node *child(Node *n,const char *name) {
    size_t i; if(n) for(i=0;i<n->count;i++) if(named(n->children[i],name)) return n->children[i];
    return NULL;
}
static const char *temp(void) { return format("t%u",++temp_id); }
static const char *label(void) { return format("label%u",++label_id); }
static Value value(const char *operand,Shape *type) { Value v; v.operand=operand;v.type=type;return v; }
static Variable *lookup(const char *source) {
    Variable *v; for(v=variables;v;v=v->next) if(!strcmp(source,v->source)) return v;
    /* Semantic analysis has already rejected every undefined identifier. */
    fputs("Internal error: missing IR symbol.\n",stderr); exit(2);
}
static Variable *declarator(Node *n,Shape *base,int reference) {
    if(n->count==1) {
        Variable *v=alloc(sizeof(*v)); v->source=n->children[0]->text;
        v->name=format("v%u",++var_id); v->type=base;v->reference=reference&&base->element;
        v->next=variables;variables=v;return v;
    } else {
        Shape *a=alloc(sizeof(*a));a->element=base;a->size=(long)n->children[2]->integer*base->size;
        return declarator(n->children[0],a,reference);
    }
}
static int check(Node *n) {
    size_t i; int code;
    if(!n) return 0;
    if(named(n,"STRUCT")) return 1;
    if(named(n,"FLOAT") || (named(n,"TYPE")&&!strcmp(n->text,"float"))) return 2;
    if(named(n,"ParamDec")) {
        Node *v=child(n,"VarDec");
        if(v && v->count>1 && v->children[0]->count>1) return 3;
    }
    if(named(n,"VarDec")) {
        Node *v=n; unsigned long bytes=4;
        while(v->count>1) {
            unsigned long count=v->children[2]->integer;
            if(!count || count>(unsigned long)INT_MAX/bytes) return 4;
            bytes*=count;v=v->children[0];
        }
    }
    for(i=0;i<n->count;i++) { code=check(n->children[i]);if(code)return code; }
    return 0;
}
int ir_supported(Node *root) {
    int code=check(root);
    if(code==1) puts("Cannot translate: Code contains variables or parameters of structure type.");
    if(code==2) puts("Cannot translate: Code contains floating-point values or variables.");
    if(code==3) puts("Cannot translate: Code contains parameters of multi-dimensional array type.");
    if(code==4) puts("Cannot translate: Array size is zero or exceeds the supported address range.");
    return code==0;
}
static const char *binary(const char *x,const char *op,const char *y) {
    const char *t;
    if(x[0]=='#' && y[0]=='#') {
        long long a=strtoll(x+1,NULL,10),b=strtoll(y+1,NULL,10),c=0;
        int fold=a>=INT_MIN && a<=INT_MAX && b>=INT_MIN && b<=INT_MAX;
        if(fold) {
            if(!strcmp(op,"+")) c=a+b;
            else if(!strcmp(op,"-")) c=a-b;
            else if(!strcmp(op,"*")) c=a*b;
            else if(b) c=a/b; else fold=0;
        }
        if(fold && c>=INT_MIN && c<=INT_MAX) return format("#%lld",c);
    }
    if((!strcmp(op,"+")||!strcmp(op,"-"))&&!strcmp(y,"#0")) return x;
    if(!strcmp(op,"*")&&!strcmp(y,"#1")) return x;
    t=temp(); emit("%s := %s %s %s",t,x,op,y);return t;
}
static Value expression(Node *n);
static void condition(Node *n,const char *yes,const char *no);
/* For arrays this returns an address; for scalar IDs it returns a store target. */
static Value lvalue(Node *n) {
    Node *a=n->children[0];
    if(named(a,"LP")) return lvalue(n->children[1]);
    if(n->count==1) {
        Variable *v=lookup(a->text);
        return value(v->type->element ? (v->reference?v->name:format("&%s",v->name)) : v->name,v->type);
    } else {
        Value base=expression(a),index=expression(n->children[2]);
        const char *offset=binary(index.operand,"*",format("#%ld",base.type->element->size));
        const char *address=binary(base.operand,"+",offset);
        /* Loads/stores use a plain address temporary, not *&variable. */
        if(address[0]=='&') { const char *t=temp();emit("%s := %s",t,address);address=t; }
        return value(base.type->element->element?address:format("*%s",address),base.type->element);
    }
}
static void copy_array(Value destination,Value source) {
    long size=destination.type->size<source.type->size?destination.type->size:source.type->size;
    const char *i=temp(),*loop=label(),*done=label(),*dst=temp(),*src=temp(),*v=temp();
    emit("%s := #0",i);emit("LABEL %s :",loop);
    emit("IF %s >= #%ld GOTO %s",i,size,done);
    emit("%s := %s + %s",dst,destination.operand,i);
    emit("%s := %s + %s",src,source.operand,i);
    emit("%s := *%s",v,src);emit("*%s := %s",dst,v);
    emit("%s := %s + #4",i,i);emit("GOTO %s",loop);emit("LABEL %s :",done);
}
static Value expression(Node *n) {
    Node *a=n->children[0],*op=n->count>1?n->children[1]:NULL;
    Value x,y; const char *t;
    if(n->count==1) {
        if(named(a,"INT")) return value(format("#%lu",a->integer),&scalar);
        x=lvalue(n);
        if(x.type->element) return x;
        t=temp(); emit("%s := %s",t,x.operand); return value(t,&scalar);
    }
    if(named(a,"LP")) return expression(op);
    if(named(a,"ID")) {
        Node *args=child(n,"Args");Argument *list=NULL,*p;
        while(args) {
            x=expression(args->children[0]);p=alloc(sizeof(*p));p->value=x.operand;
            p->next=list;list=p;args=child(args,"Args");
        }
        if(!strcmp(a->text,"write")) { emit("WRITE %s",list->value);return value("#0",&scalar); }
        t=temp();
        if(!strcmp(a->text,"read")) emit("READ %s",t);
        else {
            for(p=list;p;p=p->next) emit("ARG %s",p->value);
            emit("%s := CALL %s",t,a->text);
        }
        return value(t,&scalar);
    }
    if(named(a,"NOT")||named(op,"AND")||named(op,"OR")||named(op,"RELOP")) {
        const char *yes=label(),*done=label();t=temp();emit("%s := #0",t);
        condition(n,yes,done);emit("LABEL %s :",yes);emit("%s := #1",t);emit("LABEL %s :",done);
        return value(t,&scalar);
    }
    if(named(a,"MINUS")) { x=expression(op);return value(binary("#0","-",x.operand),&scalar); }
    if(named(op,"LB")) {
        x=lvalue(n);if(x.type->element)return x;
        t=temp();emit("%s := %s",t,x.operand);return value(t,&scalar);
    }
    if(named(op,"ASSIGNOP")) {
        x=lvalue(a);y=expression(n->children[2]);
        if(x.type->element) {copy_array(x,y);return x;}
        emit("%s := %s",x.operand,y.operand);return y;
    }
    x=expression(a);y=expression(n->children[2]);
    return value(binary(x.operand,named(op,"PLUS")?"+":named(op,"MINUS")?"-":named(op,"STAR")?"*":"/",y.operand),&scalar);
}
static void condition(Node *n,const char *yes,const char *no) {
    Node *a=n->children[0],*op=n->count>1?n->children[1]:NULL;Value x,y;
    if(named(a,"LP")) {condition(op,yes,no);return;}
    if(named(a,"NOT")) {condition(op,no,yes);return;}
    if(named(op,"AND")||named(op,"OR")) {
        const char *middle=label();
        if(named(op,"AND")) condition(a,middle,no);else condition(a,yes,middle);
        emit("LABEL %s :",middle);condition(n->children[2],yes,no);return;
    }
    if(named(op,"RELOP")) {
        x=expression(a);y=expression(n->children[2]);
        emit("IF %s %s %s GOTO %s",x.operand,op->text,y.operand,yes);
    } else {
        x=expression(n);
        if(x.operand[0]=='#') {emit("GOTO %s",strtoll(x.operand+1,NULL,10)?yes:no);return;}
        emit("IF %s != #0 GOTO %s",x.operand,yes);
    }
    emit("GOTO %s",no);
}
static void statement(Node *n);
static void compound(Node *n) {
    Node *list,*decs;
    for(list=child(n,"DefList");list;list=child(list,"DefList")) {
        Node *def=list->children[0];
        for(decs=child(def,"DecList");decs;decs=child(decs,"DecList")) {
            Node *d=decs->children[0];Variable *v=declarator(d->children[0],&scalar,0);
            if(v->type->element) emit("DEC %s %ld",v->name,v->type->size);
            if(d->count>1) {
                Value x=expression(d->children[2]);
                if(v->type->element) copy_array(value(format("&%s",v->name),v->type),x);
                else emit("%s := %s",v->name,x.operand);
            }
        }
    }
    for(list=child(n,"StmtList");list;list=child(list,"StmtList")) statement(list->children[0]);
}
static void statement(Node *n) {
    Node *first=n->children[0];Value v;
    if(named(first,"CompSt")) compound(first);
    else if(named(first,"Exp")) (void)expression(first);
    else if(named(first,"RETURN")) {v=expression(n->children[1]);emit("RETURN %s",v.operand);}
    else if(named(first,"IF")) {
        const char *yes=label(),*no=label(),*end=n->count==7?label():no;
        condition(n->children[2],yes,no);emit("LABEL %s :",yes);statement(n->children[4]);
        if(n->count==7) emit("GOTO %s",end);
        emit("LABEL %s :",no);
        if(n->count==7) {statement(n->children[6]);emit("LABEL %s :",end);}
    } else {
        const char *start=label(),*body=label(),*end=label();emit("LABEL %s :",start);
        condition(n->children[2],body,end);emit("LABEL %s :",body);statement(n->children[4]);
        emit("GOTO %s",start);emit("LABEL %s :",end);
    }
}
void ir_generate(Node *root,FILE *output) {
    Node *list;Line *line;
    variables=NULL;allocations=NULL;head=tail=NULL;temp_id=var_id=label_id=0;
    for(list=child(root,"ExtDefList");list;list=child(list,"ExtDefList")) {
        Node *ext=list->children[0],*fun=child(ext,"FunDec"),*params;
        if(!fun) continue;
        emit("FUNCTION %s :",fun->children[0]->text);
        for(params=child(fun,"VarList");params;params=child(params,"VarList")) {
            Variable *v=declarator(child(params->children[0],"VarDec"),&scalar,1);
            emit("PARAM %s",v->name);
        }
        compound(child(ext,"CompSt"));
    }
    for(line=head;line;line=line->next) {
        /* Drop only jumps whose target is the immediately following label. */
        if(!strncmp(line->text,"GOTO ",5)&&line->next &&
           !strcmp(line->next->text,format("LABEL %s :",line->text+5))) continue;
        fprintf(output,"%s\n",line->text);
    }
    while(allocations) {Allocation *next=allocations->next;free(allocations->p);free(allocations);allocations=next;}
}
