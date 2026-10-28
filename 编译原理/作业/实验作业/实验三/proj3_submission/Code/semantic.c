#include "semantic.h"
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

typedef enum { T_ERROR, T_INT, T_FLOAT, T_ARRAY, T_STRUCT, T_FUNCTION } Kind;
typedef struct Type Type;
typedef struct Field Field;
struct Field { const char *name; Type *type; int line; Field *next; };
struct Type { Kind kind; Type *element; unsigned long size; Field *fields; };
typedef enum { S_VARIABLE, S_TAG, S_FUNCTION } SymbolKind;
typedef struct Symbol { const char *name; SymbolKind kind; Type *type; struct Symbol *next; } Symbol;
typedef struct Memory { void *value; struct Memory *next; } Memory;
typedef struct Error { int kind, line; char message[256]; struct Error *next; } Error;
typedef struct { Type *type; int lvalue; } Expr;
typedef struct Pair { const Type *a, *b; const struct Pair *next; } Pair;
#define BUCKETS 1021
static Symbol *symbols[BUCKETS];
static Memory *memory;
static Error *errors;
static Type integer_type = { T_INT, NULL, 0, NULL };
static Type float_type = { T_FLOAT, NULL, 0, NULL };
static Type error_type = { T_ERROR, NULL, 0, NULL };

static void *allocate(size_t size) {
    Memory *m = checked_malloc(sizeof(*m));
    m->value = checked_malloc(size); memset(m->value, 0, size);
    m->next = memory; memory = m; return m->value;
}
static int named(const Node *n, const char *s) { return n && strcmp(n->name,s)==0; }
static Node *child(Node *n, const char *s) {
    size_t i; if (!n) return NULL;
    for(i=0;i<n->count;i++) if(named(n->children[i],s)) return n->children[i];
    return NULL;
}
static void error(int kind, int line, const char *format, ...) {
    Error **p=&errors, *e; va_list ap;
    while(*p && (*p)->line<line) p=&(*p)->next;
    if(*p && (*p)->line==line) return;
    e=allocate(sizeof(*e)); e->kind=kind; e->line=line;
    va_start(ap,format); vsnprintf(e->message,sizeof(e->message),format,ap); va_end(ap);
    e->next=*p; *p=e;
}
static unsigned hash(const char *s) {
    unsigned h=0; while(*s) h=h*31+(unsigned char)*s++; return h%BUCKETS;
}
static Symbol *lookup(const char *name, SymbolKind kind) {
    Symbol *s; for(s=symbols[hash(name)];s;s=s->next)
        if(s->kind==kind && !strcmp(name,s->name)) return s;
    return NULL;
}
static void insert(const char *name, SymbolKind kind, Type *type) {
    unsigned h=hash(name); Symbol *s=allocate(sizeof(*s));
    s->name=name; s->kind=kind; s->type=type; s->next=symbols[h]; symbols[h]=s;
}
static Type *new_type(Kind k) { Type *t=allocate(sizeof(*t)); t->kind=k; return t; }
static int equal_rec(const Type *a,const Type *b,const Pair *seen) {
    const Pair *p; Pair pair; Field *x,*y;
    if(a==b) return 1;
    if(a->kind!=b->kind) return 0;
    for(p=seen;p;p=p->next) if(p->a==a && p->b==b) return 1;
    pair.a=a;pair.b=b;pair.next=seen;
    if(a->kind==T_ARRAY) return equal_rec(a->element,b->element,&pair);
    if(a->kind==T_STRUCT || a->kind==T_FUNCTION) {
        if(a->kind==T_FUNCTION && !equal_rec(a->element,b->element,&pair)) return 0;
        for(x=a->fields,y=b->fields;x&&y;x=x->next,y=y->next)
            if(!equal_rec(x->type,y->type,&pair)) return 0;
        return !x&&!y;
    }
    return 1;
}
static int type_equal(const Type *a,const Type *b) { return equal_rec(a,b,NULL); }
static int bad(Type *t) { return t->kind==T_ERROR; }
static int basic(Type *t) { return t->kind==T_INT || t->kind==T_FLOAT; }
static Expr expression(Node *n);
static Type *specifier(Node *n);
static void definitions(Node *n, Type *structure);
static void statement(Node *n, Type *returns);

/* Wrap dimensions while descending: int a[2][3] is array(2,array(3,int)). */
static Field *declarator(Node *n,Type *base) {
    if(n->count==1) {
        Field *f=allocate(sizeof(*f)); f->name=n->children[0]->text;
        f->line=n->line; f->type=base; return f;
    } else {
        Type *t=new_type(T_ARRAY); t->element=base; t->size=n->children[2]->integer;
        return declarator(n->children[0],t);
    }
}
static void variable(Field *f) {
    if(lookup(f->name,S_VARIABLE)||lookup(f->name,S_TAG))
        error(3,f->line,"Redefined variable \"%s\"",f->name);
    else insert(f->name,S_VARIABLE,f->type);
}
static Type *specifier(Node *n) {
    Node *s=n->children[0], *tag,*defs; Type *t; Symbol *symbol;
    if(named(s,"TYPE")) return !strcmp(s->text,"int")?&integer_type:&float_type;
    tag=child(s,"Tag");
    if(tag) {
        symbol=lookup(tag->children[0]->text,S_TAG);
        if(symbol) return symbol->type;
        error(17,tag->line,"Undefined structure \"%s\"",tag->children[0]->text);
        return &error_type;
    }
    t=new_type(T_STRUCT); defs=child(s,"DefList"); definitions(defs,t);
    tag=child(s,"OptTag");
    if(tag) {
        const char *name=tag->children[0]->text;
        if(lookup(name,S_TAG)||lookup(name,S_VARIABLE)) error(16,tag->line,"Duplicated name \"%s\"",name);
        else insert(name,S_TAG,t);
    }
    return t;
}
static void declarations(Node *list,Type *base,Type *structure) {
    while(list) {
        Node *dec=list->children[0]; Field *f=declarator(dec->children[0],base);
        if(structure) {
            Field **p=&structure->fields;
            while(*p && strcmp((*p)->name,f->name)) p=&(*p)->next;
            if(*p) error(15,f->line,"Redefined field \"%s\"",f->name);
            else *p=f;
            if(dec->count>1) error(15,f->line,"Field \"%s\" cannot be initialized",f->name);
        } else {
            variable(f);
            if(dec->count>1) {
                Expr rhs=expression(dec->children[2]);
                if(!bad(base)&&!bad(rhs.type)&&!type_equal(f->type,rhs.type))
                    error(5,dec->line,"Type mismatched for assignment");
            }
        }
        list=child(list,"DecList");
    }
}
static void definitions(Node *list,Type *structure) {
    while(list) {
        Node *d=list->children[0]; Type *t=specifier(d->children[0]);
        declarations(child(d,"DecList"),t,structure); list=child(list,"DefList");
    }
}
static Expr result(Type *t,int lv) { Expr e; e.type=t; e.lvalue=lv; return e; }
static Expr expression(Node *n) {
    Node *a=n->children[0],*op=n->count>1?n->children[1]:NULL;
    Expr x,y; Symbol *s; Field *f;
    if(n->count==1) {
        if(named(a,"INT")) return result(&integer_type,0);
        if(named(a,"FLOAT")) return result(&float_type,0);
        s=lookup(a->text,S_VARIABLE);
        if(!s) { error(1,a->line,"Undefined variable \"%s\"",a->text); return result(&error_type,0); }
        return result(s->type,1);
    }
    if(named(a,"ID")) {
        Node *args=child(n,"Args"); int mismatch=0, poisoned=0;
        s=lookup(a->text,S_FUNCTION);
        if(!s) error(lookup(a->text,S_VARIABLE)?11:2,a->line,"%s function \"%s\"",lookup(a->text,S_VARIABLE)?"Not a":"Undefined",a->text);
        f=s?s->type->fields:NULL;
        while(args) {
            x=expression(args->children[0]);
            if(bad(x.type)) poisoned=1;
            else if(!f || !type_equal(f->type,x.type)) mismatch=1;
            if(f) f=f->next;
            args=child(args,"Args");
        }
        if(f) mismatch=1;
        if(s && mismatch && !poisoned) error(9,n->line,"Function arguments do not match \"%s\"",a->text);
        return result(s&&!mismatch&&!poisoned?s->type->element:&error_type,0);
    }
    if(named(a,"LP")) return expression(op);
    if(n->count==2) {
        x=expression(op);
        if(bad(x.type)) return x;
        if(!basic(x.type)||(named(a,"NOT")&&x.type->kind!=T_INT)) {
            error(7,n->line,"Type mismatched for operands"); return result(&error_type,0);
        }
        return result(x.type,0);
    }
    x=expression(a);
    if(named(op,"DOT")) {
        if(bad(x.type)) return x;
        if(x.type->kind!=T_STRUCT) { error(13,n->line,"Illegal use of dot"); return result(&error_type,0); }
        for(f=x.type->fields;f;f=f->next) if(!strcmp(f->name,n->children[2]->text)) return result(f->type,x.lvalue);
        error(14,n->line,"Non-existent field \"%s\"",n->children[2]->text); return result(&error_type,0);
    }
    y=expression(n->children[2]);
    if(named(op,"LB")) {
        if(!bad(x.type)&&x.type->kind!=T_ARRAY) error(10,n->line,"Indexed expression is not an array");
        else if(!bad(y.type)&&y.type->kind!=T_INT) error(12,n->children[2]->line,"Array index is not an integer");
        if(bad(x.type)||bad(y.type)||x.type->kind!=T_ARRAY||y.type->kind!=T_INT) return result(&error_type,0);
        return result(x.type->element,x.lvalue);
    }
    if(bad(x.type)||bad(y.type)) return result(&error_type,0);
    if(named(op,"ASSIGNOP")) {
        if(!x.lvalue) error(6,n->line,"The left-hand side of an assignment must be a variable");
        else if(!type_equal(x.type,y.type)) error(5,n->line,"Type mismatched for assignment");
        else return result(x.type,0);
        return result(&error_type,0);
    }
    if(!basic(x.type)||!type_equal(x.type,y.type)||
       ((named(op,"AND")||named(op,"OR"))&&x.type->kind!=T_INT)) {
        error(7,n->line,"Type mismatched for operands"); return result(&error_type,0);
    }
    return result(named(op,"RELOP")?&integer_type:x.type,0);
}
static void compound(Node *n,Type *returns) {
    Node *list; definitions(child(n,"DefList"),NULL);
    for(list=child(n,"StmtList");list;list=child(list,"StmtList")) statement(list->children[0],returns);
}
static void statement(Node *n,Type *returns) {
    Node *first=n->children[0]; Expr e;
    if(named(first,"CompSt")) compound(first,returns);
    else if(named(first,"Exp")) (void)expression(first);
    else if(named(first,"RETURN")) {
        e=expression(n->children[1]);
        if(!bad(e.type)&&!bad(returns)&&!type_equal(e.type,returns)) error(8,n->line,"Type mismatched for return");
    } else {
        e=expression(n->children[2]);
        if(!bad(e.type)&&e.type->kind!=T_INT) error(7,n->children[2]->line,"Condition must have integer type");
        statement(n->children[4],returns);
        if(n->count==7) statement(n->children[6],returns);
    }
}
static void external(Node *n) {
    Type *base=specifier(n->children[0]); Node *fun=child(n,"FunDec"), *list;
    if(fun) {
        Type *t=new_type(T_FUNCTION); Field **tail=&t->fields; const char *name=fun->children[0]->text;
        t->element=base;
        for(list=child(fun,"VarList");list;list=child(list,"VarList")) {
            Node *param=list->children[0]; Type *pt=specifier(param->children[0]);
            Field *f=declarator(param->children[1],pt); variable(f); *tail=f; tail=&f->next;
        }
        if(lookup(name,S_FUNCTION)) error(4,fun->line,"Redefined function \"%s\"",name);
        else insert(name,S_FUNCTION,t);
        compound(child(n,"CompSt"),base);
    } else {
        for(list=child(n,"ExtDecList");list;list=child(list,"ExtDecList")) variable(declarator(list->children[0],base));
    }
}
int semantic_analyze(Node *root) {
    Node *list; Error *e;
    int valid;
    Type *read_type, *write_type; Field *parameter;
    memset(symbols,0,sizeof(symbols)); errors=NULL; memory=NULL;
    read_type=new_type(T_FUNCTION); read_type->element=&integer_type;
    insert("read",S_FUNCTION,read_type);
    write_type=new_type(T_FUNCTION); write_type->element=&integer_type;
    parameter=allocate(sizeof(*parameter)); parameter->type=&integer_type;
    write_type->fields=parameter; insert("write",S_FUNCTION,write_type);
    for(list=child(root,"ExtDefList");list;list=child(list,"ExtDefList")) external(list->children[0]);
    for(e=errors;e;e=e->next) printf("Error type %d at Line %d: %s.\n",e->kind,e->line,e->message);
    valid=errors==NULL;
    while(memory) { Memory *next=memory->next; free(memory->value); free(memory); memory=next; }
    errors=NULL;
    return valid;
}
