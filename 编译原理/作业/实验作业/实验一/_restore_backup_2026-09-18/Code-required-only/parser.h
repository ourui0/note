#ifndef PARSER_H
#define PARSER_H

#include <stddef.h>
#include <stdio.h>

typedef enum { NODE_SYNTAX, NODE_TOKEN, NODE_TEXT, NODE_INT, NODE_FLOAT } NodeKind;

typedef struct Node {
    const char *name;
    NodeKind kind;
    int line;
    char *text;
    unsigned long integer;
    float real;
    size_t count;
    struct Node *children[8];
    struct Node *allocation_next;
} Node;

Node *node_token(const char *name, NodeKind kind, int line, const char *text);
Node *node_branch(const char *name, int count, ...);
void tree_print(const Node *root, FILE *out);
void tree_free_all(void);
void *checked_malloc(size_t size);

void diagnostic_add(char type, int line, const char *message);
int diagnostic_count(void);
int diagnostic_has(int line);
void diagnostic_print(FILE *out);
void diagnostic_free(void);

#endif
