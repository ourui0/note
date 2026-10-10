# 实验二验证

执行 `python3 tests/run_tests.py`：在临时目录编译副本，检查错误编号、行号、stdout/stderr 和退出码，不污染提交源码。

安装 pypdf 后，该脚本还直接从课程 PDF 提取 23 个原样例，总计运行 86 项测试。没有 pypdf 时只运行 63 项独立边界测试，并显示跳过提示。

执行 `LAB2_CFLAGS='-fsanitize=address,undefined -g -O1' python3 tests/run_tests.py` 进行地址和未定义行为检查。

执行 `python3 tests/package_submission.py` 打包并验证实际 ZIP：根目录清单、PDF 页数和最小字号，以及解压后源码的完整回归测试。需要 pypdf。

最终只提交实验二目录内的 `proj2_submission.zip`。测试脚本、报告源文件、课程材料及开发记录不放入 ZIP。
