#ifndef IR_H
#define IR_H
#include "parser.h"
int ir_supported(Node *root);
void ir_generate(Node *root, FILE *output);
#endif
