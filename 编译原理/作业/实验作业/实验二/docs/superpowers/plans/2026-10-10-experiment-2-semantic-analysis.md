# Experiment 2 Semantic Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and package a C-- semantic analyzer that reports required semantic errors 1-17 and implements only optional requirement 2.3 (structural equivalence for structures).

**Architecture:** Reuse the Experiment 1 Flex/Bison parser and AST, add a separate `semantic.c/.h` module, and invoke it only after successful lexical and syntax analysis. The semantic module uses a hash symbol table, recursive type objects, source-order AST traversal, poison/error types for cascade suppression, and one shared type-equivalence function implementing optional 2.3.

**Tech Stack:** C99, GNU Flex 2.6.4, GNU Bison 3.5.1, GCC 7.5, POSIX shell tests, ReportLab PDF generation, Poppler visual verification.

**Spec:** `docs/superpowers/specs/2026-10-10-experiment-2-semantic-analysis-design.md`

## Global Constraints

- Build must remain compatible with Ubuntu 20.04, GCC 7.5, Flex 2.6.4, Bison 3.5.1, and the supplied `makefile_ref`.
- Use only C standard-library facilities; no GLib or third-party C libraries.
- Semantic-valid input produces no output; all lexical, syntax, and semantic diagnostics go to `stdout`; analyzed source files exit with status 0.
- Implement required semantic errors 1-17 and only optional 2.3; do not implement optional 2.1 or 2.2.
- Preserve Experiment 1 optional comment support while continuing to reject octal/hexadecimal integers and exponent-form floats.
- The PDF report must be at most three pages and use no body text below Chinese five-size or English 11 pt.
- Final ZIP top level contains exactly `Code/` and `report.pdf`.

## Review Focus

- A recursive function must see its own signature, while a call to a later undeclared function must report error 2; Task 2 includes both tests.
- An undefined subexpression must not trigger secondary assignment/operator/return errors; Task 3 includes cascade-suppression tests.
- Array type equivalence ignores lengths but preserves dimension count and base type; Task 3 includes positive and negative cases.
- Structural equivalence ignores tag and field names but preserves ordered recursive field types; Task 4 includes assignment and argument tests.
- Unselected options must remain detectably absent; Task 4 tests function declarations as syntax errors and cross-function duplicate variables as error 3.

---

### Task 1: Establish the Experiment 2 baseline and silent semantic entry point

**Files:**
- Create: `proj2_submission/Code/parser.h`
- Create: `proj2_submission/Code/lexer.l`
- Create: `proj2_submission/Code/parser.y`
- Create: `proj2_submission/Code/parser.c`
- Create: `proj2_submission/Code/semantic.h`
- Create: `proj2_submission/Code/semantic.c`
- Create: `Makefile_ref`
- Create: `tests/run_tests.sh`

**Interfaces:**
- Consumes: Experiment 1 final `Node`, parser diagnostics, lexer, and grammar.
- Produces: `void semantic_analyze(Node *root)` and a portable test build that compiles every production `.c` file with the generated parser.

- [ ] **Step 1: Copy the Experiment 1 four-file baseline and `Makefile_ref` into the Experiment 2 paths without changing their content.**

- [ ] **Step 2: Write the first failing tests in `tests/run_tests.sh`.**

  Add `valid_empty_output` for `int main(){ return 0; }`, asserting exit 0 and byte-empty stdout; add `syntax_error_still_prints` for a missing semicolon, asserting an `Error type B` line on stdout. The portable build must use Flex/Bison, compile `parser.c` and `semantic.c`, and avoid requiring macOS `libfl`.

- [ ] **Step 3: Run the tests and verify the valid case fails because the Experiment 1 driver prints an AST.**

  Run: `bash tests/run_tests.sh valid_empty_output syntax_error_still_prints`

  Expected: build succeeds; `valid_empty_output` fails with output beginning `Program`; syntax diagnostic test passes.

- [ ] **Step 4: Add the semantic entry point and switch the driver.**

  Declare `void semantic_analyze(Node *root);` in `semantic.h`; define a no-op implementation in `semantic.c`; include it from `parser.c`; replace successful `tree_print` with `semantic_analyze(syntax_root)`. Keep lexical/syntax diagnostics and final return 0 unchanged.

- [ ] **Step 5: Re-run the focused tests and full test script.**

  Run: `bash tests/run_tests.sh valid_empty_output syntax_error_still_prints && bash tests/run_tests.sh`

  Expected: all currently registered tests pass with no compiler warnings.

- [ ] **Step 6: Commit Task 1.**

  ```bash
  git add 编译原理/作业/第二次作业/实验二
  git commit -m "feat: establish experiment 2 semantic baseline"
  ```

### Task 2: Implement types, symbol registration, and definition errors

**Files:**
- Modify: `proj2_submission/Code/semantic.h`
- Modify: `proj2_submission/Code/semantic.c`
- Modify: `tests/run_tests.sh`

**Interfaces:**
- Consumes: `Node` AST shapes from `parser.y` and `semantic_analyze(Node *root)` from Task 1.
- Produces: internal `Type`, `Field`, `Symbol`, and `ExprResult` representations; `type_equal(const Type *, const Type *)`; source-order definition traversal; errors 1-4 and 15-17.

- [ ] **Step 1: Add failing tests for symbol lookup and top-level registration.**

  Register separate fixtures for undefined variable (1), undefined function (2), variable/parameter redefinition and variable-vs-struct collision (3), duplicate function (4), recursive function success, and later-function call failure. Assert exact error number and line; success fixtures assert empty stdout.

- [ ] **Step 2: Run the Task 2 focused tests and verify each new case fails for the expected missing-semantic-analysis reason.**

  Run: `bash tests/run_tests.sh semantic_symbols`

  Expected: required error assertions fail because stdout is empty.

- [ ] **Step 3: Implement the semantic type and symbol-table core.**

  In `semantic.h`, keep only the public analyzer declaration and opaque/internal forward declarations needed by compilation. In `semantic.c`, add `TypeKind`, `BasicKind`, `Type`, `Field`, `SymbolKind`, and `Symbol`; implement allocation tracking, a fixed-bucket chained hash table, variable/function/struct lookup, and `semantic_error(int type, int line, const char *fmt, ...)` emitting `Error type %d at Line %d: ...` to stdout.

- [ ] **Step 4: Implement source-order traversal for `Program`, `ExtDefList`, `ExtDef`, `Specifier`, `StructSpecifier`, `VarDec`, `FunDec`, and parameters.**

  Register a function before analyzing its body so recursion succeeds; do not pre-collect later functions. Insert all ordinary variables and parameters into one persistent global namespace.

- [ ] **Step 5: Add failing tests for structure-definition errors.**

  Register duplicate/initialized fields (15), duplicate struct tag and tag-vs-variable collision (16), undefined struct tag (17), valid named/anonymous structs, and same field name in different structs. Assert exact error number and line.

- [ ] **Step 6: Run the structure-definition tests and verify RED.**

  Run: `bash tests/run_tests.sh semantic_struct_defs`

  Expected: new required-error assertions fail because field/tag checks are absent.

- [ ] **Step 7: Implement structure construction and definition checking.**

  Build ordered field lists without inserting fields into the ordinary-symbol table; diagnose initialization inside a structure and duplicate fields within that structure; create a unique internal identity for each anonymous structure; diagnose errors 15-17 at the declaration/reference line.

- [ ] **Step 8: Run focused and full tests.**

  Run: `bash tests/run_tests.sh semantic_symbols semantic_struct_defs && bash tests/run_tests.sh`

  Expected: all registered tests pass, valid fixtures remain byte-silent, and exit statuses are 0.

- [ ] **Step 9: Commit Task 2.**

  ```bash
  git add 编译原理/作业/第二次作业/实验二/proj2_submission/Code/semantic.* 编译原理/作业/第二次作业/实验二/tests/run_tests.sh
  git commit -m "feat: add semantic types and symbol definitions"
  ```

### Task 3: Implement expressions, statements, and errors 5-14

**Files:**
- Modify: `proj2_submission/Code/semantic.c`
- Modify: `tests/run_tests.sh`

**Interfaces:**
- Consumes: Task 2 type objects, symbol lookup, `type_equal`, and AST definition traversal.
- Produces: `analyze_exp(Node *) -> ExprResult`, argument matching, statement analysis, initializer analysis, and errors 5-14 with poison-based cascade suppression.

- [ ] **Step 1: Add failing tests for assignment, operator, return, and call errors.**

  Register errors 5-9 individually, including non-lvalue forms `(a+b)=1` and literal assignment; valid arithmetic for same-type ints/floats; invalid mixed arithmetic; integer-only logical/condition tests; correct and incorrect argument lists. Add an undefined-variable-in-expression fixture that must print only error 1, not derived errors 5/7/8.

- [ ] **Step 2: Run the expression tests and verify RED.**

  Run: `bash tests/run_tests.sh semantic_expr_core`

  Expected: new required-error assertions fail because expression typing is absent.

- [ ] **Step 3: Implement expression and statement analysis.**

  Implement literals, identifiers, parentheses, unary/binary operators, assignment, function calls, initialization, `return`, `if`, and `while`. `ExprResult` carries `Type *type`, `int is_lvalue`, and `int poisoned`; poisoned children suppress only directly derived diagnostics while sibling expressions are still visited.

- [ ] **Step 4: Re-run `semantic_expr_core` and verify GREEN.**

  Run: `bash tests/run_tests.sh semantic_expr_core`

  Expected: all core expression fixtures pass with exact error numbers and no duplicate cascade output.

- [ ] **Step 5: Add failing tests for arrays and structure access.**

  Register errors 10-14; valid one- and two-dimensional indexing; non-int index; dot access on non-struct; missing field; arrays with different sizes but equal type; arrays with different dimensions or base types and unequal type.

- [ ] **Step 6: Run the access tests and verify RED.**

  Run: `bash tests/run_tests.sh semantic_access`

  Expected: new array/field diagnostics fail because access typing is absent.

- [ ] **Step 7: Implement array indexing and structure-field access.**

  Return array element types one dimension at a time; preserve lvalue status for indexed variables and fields; check error 10 before 12 for an invalid base, and error 13 before field lookup for a non-structure base.

- [ ] **Step 8: Run focused and full tests.**

  Run: `bash tests/run_tests.sh semantic_expr_core semantic_access && bash tests/run_tests.sh`

  Expected: every registered error 1-17 fixture and all valid fixtures pass.

- [ ] **Step 9: Commit Task 3.**

  ```bash
  git add 编译原理/作业/第二次作业/实验二/proj2_submission/Code/semantic.c 编译原理/作业/第二次作业/实验二/tests/run_tests.sh
  git commit -m "feat: implement semantic expression checking"
  ```

### Task 4: Implement only optional 2.3 and lock the option boundaries

**Files:**
- Modify: `proj2_submission/Code/semantic.c`
- Modify: `tests/run_tests.sh`

**Interfaces:**
- Consumes: the shared `type_equal` call sites from Tasks 2-3.
- Produces: recursive ordered structural equivalence for structures, array equivalence that ignores lengths, and regression proof that options 2.1/2.2 remain unimplemented.

- [ ] **Step 1: Add failing optional-2.3 tests.**

  Add positive assignment/return/argument fixtures where differently named structs have the same ordered field-type sequence and different field names; add negative fixtures for field count, field order, nested field type, and array dimension differences. Positive cases assert empty stdout; negatives assert the applicable required error 5, 8, or 9.

- [ ] **Step 2: Run the optional test group and verify RED.**

  Run: `bash tests/run_tests.sh optional_23`

  Expected: at least the different-tag positive cases fail under nominal-equivalence behavior.

- [ ] **Step 3: Implement recursive structural equivalence in the one shared `type_equal` function.**

  Ignore structure tag and field names; compare ordered field counts and recursively compare field types; compare arrays by nesting and base type while ignoring lengths; track active type pairs to avoid recursion loops.

- [ ] **Step 4: Add and run unselected-option boundary tests.**

  Add a function-declaration fixture that must report syntax error B (2.1 absent), and duplicate local names in different functions that must report error 3 (2.2 absent). Run: `bash tests/run_tests.sh option_boundaries`.

  Expected: both fixtures demonstrate the options remain absent.

- [ ] **Step 5: Add Experiment 1 lexical-boundary regressions.**

  Confirm line/block comments are accepted in semantic-valid input; unterminated comments report A; octal/hexadecimal and exponent forms are rejected; all diagnostics use stdout and return 0.

- [ ] **Step 6: Run the full semantic and lexical suite.**

  Run: `bash tests/run_tests.sh`

  Expected: all tests pass; the summary reports zero failures.

- [ ] **Step 7: Compile using a clean copy with the supplied `makefile_ref`.**

  Run from a temporary directory containing only `Code/` plus `makefile_ref`: `make -f makefile_ref` on the course-compatible Linux environment, or the documented portable equivalent locally.

  Expected: parser binary produced without warnings or undefined symbols.

- [ ] **Step 8: Commit Task 4.**

  ```bash
  git add 编译原理/作业/第二次作业/实验二/proj2_submission/Code/semantic.c 编译原理/作业/第二次作业/实验二/tests/run_tests.sh
  git commit -m "feat: add structural equivalence optional feature"
  ```

### Task 5: Produce and verify the report and submission archive

**Files:**
- Create: `_report_source/report.md`
- Create: `_report_source/build_report.py`
- Create: `proj2_submission/report.pdf`
- Create: `proj2_submission.zip`
- Create: `tmp/pdfs/experiment2-report-*.png`

**Interfaces:**
- Consumes: verified implementation behavior, exact build commands, Typora LaTeX theme style guide, and the Experiment 1 report layout.
- Produces: a professional two-page monochrome/NJU-styled PDF and a correctly rooted submission ZIP.

- [ ] **Step 1: Write the report source.**

  Limit content to implemented functions, concise implementation highlights, explicit “only optional 2.3” scope, detailed compile/run commands, and a short test statement. Do not paste large code blocks or claim options 2.1/2.2.

- [ ] **Step 2: Start the required PDF artifact operation marker, then implement the ReportLab builder.**

  Run `node container_tools/mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format pdf` exactly once immediately before the first PDF authoring command. Adapt the Typora LaTeX theme with Songti body, Heiti headings, black/gray rules, no blue, 11 pt or larger body text, A4 layout, NJU text masthead, and page numbers.

- [ ] **Step 3: Generate the PDF and verify structural constraints.**

  Run the builder, then use `pdfinfo` and `pdftotext` to assert page count `<= 3`, required section text is present, only option 2.3 is claimed, and build commands are included.

- [ ] **Step 4: Render and inspect every PDF page.**

  Run `pdftoppm -png proj2_submission/report.pdf tmp/pdfs/experiment2-report`; inspect every PNG at original detail; revise until there is no clipping, overlap, stray blue, broken Chinese glyph, orphan heading, or undersized text.

- [ ] **Step 5: Build the final archive from the submission directory.**

  Create `proj2_submission.zip` in the Experiment 2 folder so that the archive root contains `Code/` and `report.pdf`, not `proj2_submission/`.

- [ ] **Step 6: Verify archive inventory and rebuild from extracted contents.**

  Run `unzip -l proj2_submission.zip`; reject unexpected files or extra root levels. Extract into a fresh temporary directory, compile the extracted `Code/` with `makefile_ref`/portable equivalent, run the full tests against extracted code, confirm report page count and source-file list.

- [ ] **Step 7: Run the final full verification.**

  Run: `bash tests/run_tests.sh`, clean production build, `pdfinfo`, `pdftotext` assertions, `unzip -t`, archive manifest comparison, and extracted-code smoke tests.

  Expected: every command exits 0; test summary has zero failures; PDF is at most three pages; archive contains exactly six Code source files plus `report.pdf` and directory entries.

- [ ] **Step 8: Commit Task 5.**

  ```bash
  git add 编译原理/作业/第二次作业/实验二
  git commit -m "docs: package experiment 2 submission"
  ```

