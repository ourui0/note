# 实验三测试

运行 `python3 tests/run_tests.py`，需要 Flex、Bison、C99 编译器及 Python 的 pypdf 包。测试始终编译临时副本，不将生成文件放进 Code/。

测试包含手册样例、数组引用/别名/多维寻址、短路副作用、递归、嵌套调用及 24 组原生 C 输出对照。ir_vm.py 是依据手册指令格式编写的测试解释器，不是课程官方虚拟机。原生 C 对照只选取有明确定义且不依赖求值顺序的表达式。

用 `LAB3_CFLAGS='-fsanitize=address,undefined -g -O1' python3 tests/run_tests.py` 启用编译器运行时检查。

用 `python3 tests/package_submission.py` 生成最终 ZIP，并检查归档内容、PDF 页数/字号，解压后重新编译执行测试。

选做仅 3.2；结构体原样例必须输出 `Cannot translate: Code contains variables or parameters of structure type.`。最终提交文件为上一级目录中的 proj3_submission.zip。
