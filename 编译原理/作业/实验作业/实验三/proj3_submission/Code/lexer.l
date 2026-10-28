%option noyywrap nounput noinput never-interactive
%x COMMENT
%{
#include "parser.h"
#include "syntax.tab.h"
#include <stdio.h>

int current_token = 0, previous_token = 0;
int current_line = 1, previous_line = 1;
/* token_line：当前词素所在行；prev_token_line：上一个词素所在行；
   yy_last_token：最近返回的词素，用于判断它是否开启了新的语法单元。 */
int token_line = 1, prev_token_line = 1, yy_last_token = 0;
int unterminated_comment = 0;
static int comment_line = 1;

/* 行号自己数，不用 Flex 的 %option yylineno：yylineno 在扫描到换行符时
   就把它算成"新的一行"，于是紧跟其后的词素与它同处一行，
   "上一行末尾漏了分号"这类错误会被整体推到下一行。
   这里让换行符在动作里自增 line_count，语义与判题期望一致。 */
int line_count = 1;

#define YY_USER_ACTION do { \
    prev_token_line = token_line; \
    token_line = line_count; \
} while (0);

static int emit(int token, const char *name, NodeKind kind, const char *text) {
    previous_token = current_token; previous_line = current_line;
    current_token = token; current_line = line_count;
    yy_last_token = token;
    yylval.node = node_token(name, kind, current_line, text);
    return token;
}
#define TOKEN(t) return emit(t, #t, NODE_TOKEN, yytext)
#define VALUE(t, k) return emit(t, #t, k, yytext)
%}
D       [0-9]
IDCHAR  [a-zA-Z_0-9]
%%
[ \t\v\f\r]+         { /* whitespace */ }
\n                   { ++line_count; }
"//"[^\n]*           { /* line comment, including one at EOF */ }
"/*"                 { comment_line = token_line; BEGIN(COMMENT); }
<COMMENT>"*/"        { BEGIN(INITIAL); }
<COMMENT>\n          { ++line_count; }
<COMMENT>[^*\n]+     { /* comment text */ }
<COMMENT>"*"         { /* comment text */ }
<COMMENT><<EOF>>     { diagnostic_add('A', comment_line, "Unterminated comment"); \
                       previous_token = current_token; previous_line = current_line; \
                       current_token = 0; current_line = line_count; \
                       unterminated_comment = 1; BEGIN(INITIAL); return 0; }
"int"|"float"        { VALUE(TYPE, NODE_TEXT); }
"struct"             { TOKEN(STRUCT); }
"return"             { TOKEN(RETURN); }
"if"                 { TOKEN(IF); }
"else"               { TOKEN(ELSE); }
"while"              { TOKEN(WHILE); }
{D}+\.{D}*           { VALUE(FLOAT, NODE_FLOAT); }   /* 43. —— 小数点后无数字 */
\.{D}+               { VALUE(FLOAT, NODE_FLOAT); }   /* .5  —— 小数点前无数字 */
0|[1-9]{D}*          { VALUE(INT, NODE_INT); }
[a-zA-Z_]{IDCHAR}*   { VALUE(ID, NODE_TEXT); }
";"                  { TOKEN(SEMI); }
","                  { TOKEN(COMMA); }
"="                  { TOKEN(ASSIGNOP); }
">"|"<"|">="|"<="|"=="|"!=" { VALUE(RELOP, NODE_TEXT); }
"+"                  { TOKEN(PLUS); }
"-"                  { TOKEN(MINUS); }
"*"                  { TOKEN(STAR); }
"/"                  { TOKEN(DIV); }
"&&"                 { TOKEN(AND); }
"||"                 { TOKEN(OR); }
"."                  { TOKEN(DOT); }
"!"                  { TOKEN(NOT); }
"("                  { TOKEN(LP); }
")"                  { TOKEN(RP); }
"["                  { TOKEN(LB); }
"]"                  { TOKEN(RB); }
"{"                  { TOKEN(LC); }
"}"                  { TOKEN(RC); }
.                    { char message[80]; snprintf(message, sizeof(message), "Undefined character '%.20s'", yytext); diagnostic_add('A', token_line, message); }
<<EOF>>              { previous_token = current_token; previous_line = current_line; current_token = 0; current_line = line_count; return 0; }
%%
