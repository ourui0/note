%option noyywrap nounput noinput yylineno never-interactive
%{
#include "parser.h"
#include "syntax.tab.h"
#include <stdio.h>

int current_token = 0, previous_token = 0;
int current_line = 1, previous_line = 1;

static int emit(int token, const char *name, NodeKind kind, const char *text) {
    previous_token = current_token; previous_line = current_line;
    current_token = token; current_line = yylineno;
    yylval.node = node_token(name, kind, current_line, text);
    return token;
}
#define TOKEN(t) return emit(t, #t, NODE_TOKEN, yytext)
#define VALUE(t, k) return emit(t, #t, k, yytext)
static int bad_number(const char *description) {
    char message[200];
    snprintf(message, sizeof(message), "%s '%.100s'", description, yytext);
    diagnostic_add('A', yylineno, message);
    /* Keep a placeholder token so one lexical error does not destroy a statement. */
    return emit(INT, "INT", NODE_INT, "0");
}
%}
D       [0-9]
IDCHAR  [a-zA-Z_0-9]
%%
[ \t\v\f\r]+         { /* whitespace */ }
\n                     { /* yylineno is maintained by Flex. */ }
"int"|"float"         { VALUE(TYPE, NODE_TEXT); }
"struct"              { TOKEN(STRUCT); }
"return"              { TOKEN(RETURN); }
"if"                  { TOKEN(IF); }
"else"                { TOKEN(ELSE); }
"while"               { TOKEN(WHILE); }
{D}+\.{D}+             { VALUE(FLOAT, NODE_FLOAT); }
{D}+\.                 { return bad_number("A plain float needs digits on both sides of the point"); }
{D}+[a-zA-Z_]{IDCHAR}* { return bad_number("Illegal numeric token"); }
0|[1-9]{D}*           { VALUE(INT, NODE_INT); }
[a-zA-Z_]{IDCHAR}*    { VALUE(ID, NODE_TEXT); }
";"                   { TOKEN(SEMI); }
","                   { TOKEN(COMMA); }
"="                   { TOKEN(ASSIGNOP); }
">"|"<"|">="|"<="|"=="|"!=" { TOKEN(RELOP); }
"+"                   { TOKEN(PLUS); }
"-"                   { TOKEN(MINUS); }
"*"                   { TOKEN(STAR); }
"/"                   { TOKEN(DIV); }
"&&"                  { TOKEN(AND); }
"||"                  { TOKEN(OR); }
"."                   { TOKEN(DOT); }
"!"                   { TOKEN(NOT); }
"("                   { TOKEN(LP); }
")"                   { TOKEN(RP); }
"["                   { TOKEN(LB); }
"]"                   { TOKEN(RB); }
"{"                   { TOKEN(LC); }
"}"                   { TOKEN(RC); }
.                     { char message[80]; snprintf(message, sizeof(message), "Undefined character '%.20s'", yytext); diagnostic_add('A', yylineno, message); }
<<EOF>>               { previous_token = current_token; previous_line = current_line; current_token = 0; current_line = yylineno; return 0; }
%%
