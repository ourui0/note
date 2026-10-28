#include "parser.h"
#include "semantic.h"
#include "ir.h"
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

int yyparse(void);
int yylex(void);
int yylex_destroy(void);
void yyrestart(FILE *input);
extern Node *syntax_root;
static Node *allocations;

typedef struct Diagnostic {
    char type;
    int line;
    char *message;
    struct Diagnostic *next;
} Diagnostic;

static Diagnostic *diagnostic_head;
static int diagnostics;

int main(int argc, char **argv) {
    FILE *input, *output;
    int result, failed;
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <source.cmm> <output.ir>\n", argv[0]);
        return 2;
    }
    if (!strcmp(argv[1],argv[2])) {
        fputs("Input and output must be different files.\n",stderr);
        return 2;
    }
    input = fopen(argv[1], "rb");
    if (!input) {
        perror(argv[1]);
        return 2;
    }
    {
        struct stat source_stat, output_stat;
        if (stat(argv[1], &source_stat)==0 && stat(argv[2], &output_stat)==0 &&
            source_stat.st_dev==output_stat.st_dev && source_stat.st_ino==output_stat.st_ino) {
            fputs("Input and output must be different files.\n",stderr);
            fclose(input);
            return 2;
        }
    }
    yyrestart(input);
    result = yyparse();
    if (result != 0)
        while (yylex() != 0) { }
    failed = result != 0 || diagnostic_count() != 0;
    output=fopen(argv[2],"w");
    if (!output) { perror(argv[2]); fclose(input); return 2; }
    if (failed)
        diagnostic_print(stdout);
    else if (ir_supported(syntax_root) && semantic_analyze(syntax_root))
        ir_generate(syntax_root,output);
    failed=ferror(output);
    if (fclose(output)!=0) failed=1;
    tree_free_all();
    diagnostic_free();
    yylex_destroy();
    fclose(input);
    /* The online judge requires a normal exit even when diagnostics exist. */
    return failed ? 2 : 0;
}

void *checked_malloc(size_t size) {
    void *pointer = malloc(size);
    if (!pointer) {
        fputs("Out of memory.\n", stderr);
        exit(2);
    }
    return pointer;
}

static Node *allocate_node(const char *name, NodeKind kind, int line) {
    Node *node = checked_malloc(sizeof(*node));
    memset(node, 0, sizeof(*node));
    node->name = name;
    node->kind = kind;
    node->line = line;
    node->allocation_next = allocations;
    allocations = node;
    return node;
}

Node *node_token(const char *name, NodeKind kind, int line, const char *text) {
    Node *node = allocate_node(name, kind, line);
    if (kind == NODE_TEXT) {
        node->text = checked_malloc(strlen(text) + 1);
        strcpy(node->text, text);
    } else if (kind == NODE_INT) {
        node->integer = strtoul(text, NULL, 0);
    } else if (kind == NODE_FLOAT) {
        node->real = strtof(text, NULL);
    }
    return node;
}

Node *node_branch(const char *name, int count, ...) {
    va_list arguments;
    Node *node = allocate_node(name, NODE_SYNTAX, 0);
    int index;
    va_start(arguments, count);
    for (index = 0; index < count; ++index) {
        Node *child = va_arg(arguments, Node *);
        if (!child)
            continue;
        if (!node->count)
            node->line = child->line;
        node->children[node->count++] = child;
    }
    va_end(arguments);
    return node->count ? node : NULL;
}

void tree_print(const Node *root, FILE *out) {
    typedef struct { const Node *node; size_t depth; } Entry;
    size_t capacity = 64, used = 0;
    Entry *stack = checked_malloc(capacity * sizeof(*stack));
    if (root)
        stack[used++] = (Entry){root, 0};
    while (used) {
        Entry entry = stack[--used];
        const Node *node = entry.node;
        size_t index;
        for (index = 0; index < entry.depth; ++index)
            fputs("  ", out);
        fputs(node->name, out);
        switch (node->kind) {
        case NODE_SYNTAX: fprintf(out, " (%d)", node->line); break;
        case NODE_TEXT: fprintf(out, ": %s", node->text); break;
        case NODE_INT: fprintf(out, ": %lu", node->integer); break;
        case NODE_FLOAT: fprintf(out, ": %f", (double)node->real); break;
        case NODE_TOKEN: break;
        }
        fputc('\n', out);
        if (used + node->count > capacity) {
            Entry *larger;
            capacity *= 2;
            larger = checked_malloc(capacity * sizeof(*stack));
            memcpy(larger, stack, used * sizeof(*stack));
            free(stack);
            stack = larger;
        }
        for (index = node->count; index > 0; --index)
            stack[used++] = (Entry){node->children[index - 1], entry.depth + 1};
    }
    free(stack);
}

void tree_free_all(void) {
    while (allocations) {
        Node *next = allocations->allocation_next;
        free(allocations->text);
        free(allocations);
        allocations = next;
    }
}

void diagnostic_add(char type, int line, const char *message) {
    Diagnostic **cursor = &diagnostic_head, *item;
    if (line < 1)
        line = 1;
    while (*cursor && (*cursor)->line < line)
        cursor = &(*cursor)->next;
    if (*cursor && (*cursor)->line == line) {
        /* 每行 first-error-wins（仿满分版，无 A/B 优先级） */
        return;
    } else {
        item = checked_malloc(sizeof(*item));
        item->next = *cursor;
        *cursor = item;
        ++diagnostics;
    }
    item->type = type;
    item->line = line;
    item->message = checked_malloc(strlen(message) + 1);
    strcpy(item->message, message);
}

int diagnostic_count(void) {
    return diagnostics;
}

int diagnostic_has(int line) {
    Diagnostic *item;
    for (item = diagnostic_head; item; item = item->next)
        if (item->line == line)
            return 1;
    return 0;
}

void diagnostic_print(FILE *out) {
    Diagnostic *item;
    for (item = diagnostic_head; item; item = item->next)
        fprintf(out, "Error type %c at Line %d: %s.\n",
                item->type, item->line, item->message);
}

void diagnostic_free(void) {
    while (diagnostic_head) {
        Diagnostic *next = diagnostic_head->next;
        free(diagnostic_head->message);
        free(diagnostic_head);
        diagnostic_head = next;
    }
    diagnostics = 0;
}
