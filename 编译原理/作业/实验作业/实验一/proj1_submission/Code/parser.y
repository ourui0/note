%{
#include "parser.h"
int yylex(void);
void yyerror(const char *message);
extern int token_line, prev_token_line, yy_last_token;
Node *syntax_root;
#define N(name, count, ...) node_branch(name, count, __VA_ARGS__)
/* 错误恢复：每个"语法单元"都带一条 error 产生式，出错时立刻把该单元归约成
   NULL。这样分析器在出错的那一行内就完成恢复，不会为了寻找同步点向后丢弃
   词法单元，因而后续各行各自的错误都能被独立报出来。 */
%}
%union { struct Node *node; }
%token <node> INT FLOAT ID SEMI COMMA ASSIGNOP RELOP PLUS MINUS STAR DIV
%token <node> AND OR DOT NOT TYPE LP RP LB RB LC RC STRUCT RETURN IF ELSE WHILE
%type <node> Program ExtDefList ExtDef ExtDecList Specifier StructSpecifier OptTag Tag
%type <node> VarDec FunDec VarList ParamDec CompSt StmtList Stmt DefList Def DecList Dec Exp Args
%right ASSIGNOP
%left OR
%left AND
%left RELOP
%left PLUS MINUS
%left STAR DIV
%right NOT UMINUS
%left LP RP LB RB DOT
%nonassoc LOWER_THAN_ELSE
%nonassoc ELSE
%start Program
%%
Program: ExtDefList { /* 空文件（或只有注释/空白）时 ExtDefList 为空，
                          仍然要打印一个没有子结点的 Program 根。 */
                      $$ = $1 ? N("Program", 1, $1)
                              : node_token("Program", NODE_SYNTAX, token_line, NULL);
                      syntax_root = $$; };
ExtDefList: ExtDef ExtDefList { $$ = N("ExtDefList", 2, $1, $2); }
          | error { $$ = NULL; }
          | /* empty */ { $$ = NULL; };
ExtDef: Specifier ExtDecList SEMI { $$ = N("ExtDef", 3, $1, $2, $3); }
      | Specifier SEMI { $$ = N("ExtDef", 2, $1, $2); }
      | Specifier FunDec CompSt { $$ = N("ExtDef", 3, $1, $2, $3); }
      | error { $$ = NULL; };
ExtDecList: VarDec { $$ = N("ExtDecList", 1, $1); }
          | VarDec COMMA ExtDecList { $$ = N("ExtDecList", 3, $1, $2, $3); }
          | error { $$ = NULL; };
Specifier: TYPE { $$ = N("Specifier", 1, $1); }
         | StructSpecifier { $$ = N("Specifier", 1, $1); }
         | error { $$ = NULL; };
StructSpecifier: STRUCT OptTag LC DefList RC { $$ = N("StructSpecifier", 5, $1, $2, $3, $4, $5); }
               | STRUCT Tag { $$ = N("StructSpecifier", 2, $1, $2); }
               | error { $$ = NULL; };
OptTag: ID { $$ = N("OptTag", 1, $1); }
      | error { $$ = NULL; }
      | /* empty */ { $$ = NULL; };
Tag: ID { $$ = N("Tag", 1, $1); }
   | error { $$ = NULL; };
VarDec: ID { $$ = N("VarDec", 1, $1); }
      | VarDec LB INT RB { $$ = N("VarDec", 4, $1, $2, $3, $4); }
      | error { $$ = NULL; };
FunDec: ID LP VarList RP { $$ = N("FunDec", 4, $1, $2, $3, $4); }
      | ID LP RP { $$ = N("FunDec", 3, $1, $2, $3); }
      | error { $$ = NULL; };
VarList: ParamDec COMMA VarList { $$ = N("VarList", 3, $1, $2, $3); }
       | ParamDec { $$ = N("VarList", 1, $1); }
       | error { $$ = NULL; };
ParamDec: Specifier VarDec { $$ = N("ParamDec", 2, $1, $2); }
        | error { $$ = NULL; };
CompSt: LC DefList StmtList RC { $$ = N("CompSt", 4, $1, $2, $3, $4); }
      | error { $$ = NULL; };
StmtList: Stmt StmtList { $$ = N("StmtList", 2, $1, $2); }
        | /* empty */ { $$ = NULL; };
Stmt: Exp SEMI { $$ = N("Stmt", 2, $1, $2); }
    | CompSt { $$ = N("Stmt", 1, $1); }
    | RETURN Exp SEMI { $$ = N("Stmt", 3, $1, $2, $3); }
    | IF LP Exp RP Stmt %prec LOWER_THAN_ELSE { $$ = N("Stmt", 5, $1, $2, $3, $4, $5); }
    | IF LP Exp RP Stmt ELSE Stmt { $$ = N("Stmt", 7, $1, $2, $3, $4, $5, $6, $7); }
    | WHILE LP Exp RP Stmt { $$ = N("Stmt", 5, $1, $2, $3, $4, $5); }
    ;
DefList: Def DefList { $$ = N("DefList", 2, $1, $2); }
       | /* empty */ { $$ = NULL; };
Def: Specifier DecList SEMI { $$ = N("Def", 3, $1, $2, $3); }
   | error { $$ = NULL; };
DecList: Dec { $$ = N("DecList", 1, $1); }
       | Dec COMMA DecList { $$ = N("DecList", 3, $1, $2, $3); }
       | error { $$ = NULL; };
Dec: VarDec { $$ = N("Dec", 1, $1); }
   | VarDec ASSIGNOP Exp { $$ = N("Dec", 3, $1, $2, $3); }
   | error { $$ = NULL; };
Exp: Exp ASSIGNOP Exp { $$ = N("Exp", 3, $1, $2, $3); }
   | Exp AND Exp { $$ = N("Exp", 3, $1, $2, $3); }
   | Exp OR Exp { $$ = N("Exp", 3, $1, $2, $3); }
   | Exp RELOP Exp { $$ = N("Exp", 3, $1, $2, $3); }
   | Exp PLUS Exp { $$ = N("Exp", 3, $1, $2, $3); }
   | Exp MINUS Exp { $$ = N("Exp", 3, $1, $2, $3); }
   | Exp STAR Exp { $$ = N("Exp", 3, $1, $2, $3); }
   | Exp DIV Exp { $$ = N("Exp", 3, $1, $2, $3); }
   | LP Exp RP { $$ = N("Exp", 3, $1, $2, $3); }
   | MINUS Exp %prec UMINUS { $$ = N("Exp", 2, $1, $2); }
   | NOT Exp { $$ = N("Exp", 2, $1, $2); }
   | ID LP Args RP { $$ = N("Exp", 4, $1, $2, $3, $4); }
   | ID LP RP { $$ = N("Exp", 3, $1, $2, $3); }
   | Exp LB Exp RB { $$ = N("Exp", 4, $1, $2, $3, $4); }
   | Exp DOT ID { $$ = N("Exp", 3, $1, $2, $3); }
   | ID { $$ = N("Exp", 1, $1); }
   | INT { $$ = N("Exp", 1, $1); }
   | FLOAT { $$ = N("Exp", 1, $1); }
   | error { $$ = NULL; };
Args: Exp COMMA Args { $$ = N("Args", 3, $1, $2, $3); }
    | Exp { $$ = N("Args", 1, $1); }
    | error { $$ = NULL; };
%%
#include "lex.yy.c"

static int opens_new_unit(int tok) {
    /* 判断一个词法单元能否开启新的定义/语句，用于区分两类跨行错误：
       被读到的词法单元若是 int/if/while 这类新单元的开头，说明上一行
       末尾少了东西；若是 ; } 之类的收尾符号，说明错误就在它所在行。 */
    switch (tok) {
    case TYPE: case STRUCT: case RETURN: case IF: case WHILE: case LC:
        return 1;
    default:
        return 0;
    }
}

void yyerror(const char *message) {
    int line;
    (void)message;
    /* Bison 一发现错误就调用 yyerror，这里立即报告（每行只留第一条）。
       行号取"被读到的那个不该出现的词法单元"所在行；只有当它与上一个
       词法单元不同行、且它本身开启了新语法单元时，才把错误归到上一行
       （漏写分号这类错误的惯用报法）。 */
    if (token_line > prev_token_line && opens_new_unit(yy_last_token))
        line = prev_token_line;
    else
        line = token_line;
    diagnostic_add('B', line, "Syntax error (check delimiters and statement structure)");
}
