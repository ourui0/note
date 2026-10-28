%{
#include "parser.h"
int yylex(void);
void yyerror(const char *message);
extern int current_token, previous_token, current_line, previous_line;
Node *syntax_root;
#define N(name, count, ...) node_branch(name, count, __VA_ARGS__)
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
Program: ExtDefList { $$ = N("Program", 1, $1); syntax_root = $$; };
ExtDefList: ExtDef ExtDefList { $$ = N("ExtDefList", 2, $1, $2); }
          | /* empty */ { $$ = NULL; };
ExtDef: Specifier ExtDecList SEMI { $$ = N("ExtDef", 3, $1, $2, $3); }
      | Specifier SEMI { $$ = N("ExtDef", 2, $1, $2); }
      | Specifier FunDec CompSt { $$ = N("ExtDef", 3, $1, $2, $3); }
      | Specifier ExtDecList error { $$ = NULL; yyerrok; }
      | error SEMI { $$ = NULL; yyerrok; };
ExtDecList: VarDec { $$ = N("ExtDecList", 1, $1); }
          | VarDec COMMA ExtDecList { $$ = N("ExtDecList", 3, $1, $2, $3); };
Specifier: TYPE { $$ = N("Specifier", 1, $1); }
         | StructSpecifier { $$ = N("Specifier", 1, $1); };
StructSpecifier: STRUCT OptTag LC DefList RC { $$ = N("StructSpecifier", 5, $1, $2, $3, $4, $5); }
               | STRUCT Tag { $$ = N("StructSpecifier", 2, $1, $2); }
               | STRUCT OptTag LC error RC { $$ = NULL; yyerrok; };
OptTag: ID { $$ = N("OptTag", 1, $1); } | /* empty */ { $$ = NULL; };
Tag: ID { $$ = N("Tag", 1, $1); };
VarDec: ID { $$ = N("VarDec", 1, $1); }
      | VarDec LB INT RB { $$ = N("VarDec", 4, $1, $2, $3, $4); }
      | VarDec LB error RB { $$ = NULL; yyerrok; }
      | VarDec LB INT error { $$ = $1; yyerrok; };
FunDec: ID LP VarList RP { $$ = N("FunDec", 4, $1, $2, $3, $4); }
      | ID LP RP { $$ = N("FunDec", 3, $1, $2, $3); }
      | ID LP error RP { $$ = NULL; yyerrok; };
VarList: ParamDec COMMA VarList { $$ = N("VarList", 3, $1, $2, $3); }
       | ParamDec { $$ = N("VarList", 1, $1); };
ParamDec: Specifier VarDec { $$ = N("ParamDec", 2, $1, $2); };
CompSt: LC DefList StmtList RC { $$ = N("CompSt", 4, $1, $2, $3, $4); }
      | LC DefList error RC { $$ = NULL; yyerrok; };
StmtList: Stmt StmtList { $$ = N("StmtList", 2, $1, $2); }
        | /* empty */ { $$ = NULL; };
Stmt: Exp SEMI { $$ = N("Stmt", 2, $1, $2); }
    | CompSt { $$ = N("Stmt", 1, $1); }
    | RETURN Exp SEMI { $$ = N("Stmt", 3, $1, $2, $3); }
    | IF LP Exp RP Stmt %prec LOWER_THAN_ELSE { $$ = N("Stmt", 5, $1, $2, $3, $4, $5); }
    | IF LP Exp RP Stmt ELSE Stmt { $$ = N("Stmt", 7, $1, $2, $3, $4, $5, $6, $7); }
    | WHILE LP Exp RP Stmt { $$ = N("Stmt", 5, $1, $2, $3, $4, $5); }
    | error SEMI { $$ = NULL; yyerrok; }
    | Exp error { $$ = NULL; yyerrok; }
    | RETURN Exp error { $$ = NULL; yyerrok; }
    | IF LP error RP Stmt %prec LOWER_THAN_ELSE { $$ = NULL; yyerrok; }
    | IF LP error RP Stmt ELSE Stmt { $$ = NULL; yyerrok; }
    | WHILE LP error RP Stmt { $$ = NULL; yyerrok; }
    | IF LP Exp error Stmt %prec LOWER_THAN_ELSE { $$ = NULL; yyerrok; }
    | IF LP Exp error Stmt ELSE Stmt { $$ = NULL; yyerrok; }
    | WHILE LP Exp error Stmt { $$ = NULL; yyerrok; };
DefList: Def DefList { $$ = N("DefList", 2, $1, $2); }
       | /* empty */ { $$ = NULL; };
Def: Specifier DecList SEMI { $$ = N("Def", 3, $1, $2, $3); }
   | Specifier DecList error { $$ = NULL; yyerrok; }
   | Specifier error SEMI { $$ = NULL; yyerrok; };
DecList: Dec { $$ = N("DecList", 1, $1); }
       | Dec COMMA DecList { $$ = N("DecList", 3, $1, $2, $3); };
Dec: VarDec { $$ = N("Dec", 1, $1); }
   | VarDec ASSIGNOP Exp { $$ = N("Dec", 3, $1, $2, $3); };
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
   | LP error RP { $$ = NULL; yyerrok; }
   | ID LP error RP { $$ = NULL; yyerrok; }
   | Exp LB error RB { $$ = NULL; yyerrok; }
   | Exp LB Exp error { $$ = $1; yyerrok; };
Args: Exp COMMA Args { $$ = N("Args", 3, $1, $2, $3); }
    | Exp { $$ = N("Args", 1, $1); };
%%
#include "lex.yy.c"

void yyerror(const char *message) {
    int line = current_line;
    (void)message;
    /* At a new line/EOF, a missing terminator belongs to the preceding
       unfinished construct, not to the next otherwise-valid statement. */
    if ((current_line > previous_line || current_token == 0)
        && previous_token != LC && previous_token != SEMI && previous_token != RC)
        line = previous_line;
    if (current_token == 0) line = previous_line;
    diagnostic_add('B', line, "Syntax error (check delimiters and statement structure)");
}
