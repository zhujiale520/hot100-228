# LeetCode 速成 · Hot 100 + 代码随想录

> 项目名：**LeetCode 速成**（Hot 100 + 代码随想录）。力扣「热题 100」+ 代码随想录补充题单，每题一句话记忆、思路要点、复杂度、易错点，外加
> 每题给**朴素解法**（最直白、能看懂怎么想出来的）和**优化解法**（能过题的写法）两段 LeetCode 代码，外加一段 **ACM 模式完整程序**。四种语言各一本，排版按学位论文规范。

| 语言 | PDF | 页数 | 大小 |
|---|---|---|---|
| Python | [leetcode-228-python.pdf](book/leetcode-228-python.pdf) | 482 | 2.5 MB |
| C++ | [leetcode-228-cpp.pdf](book/leetcode-228-cpp.pdf) | 434 | 2.4 MB |
| Java | [leetcode-228-java.pdf](book/leetcode-228-java.pdf) | 475 | 2.7 MB |
| Go | [leetcode-228-go.pdf](book/leetcode-228-go.pdf) | 505 | 2.5 MB |

## 这套书是什么

- **228 题**：力扣「热题 100」全量 100 题（17 类）+ 代码随想录题单里热题 100 之外的 128 题（11 类）。
- **每道题只有一页半到两页**，固定七块内容：
  1. 题意：一句话说清「给什么、求什么」
  2. 示例：官方用例，用来对拍
  3. **一句话记忆**：能背下来的口诀，考前只翻这个
  4. 思路要点：3~6 条，顺序就是面试口述的顺序
  5. 复杂度
  6. 易错点
  7. 三段代码：**朴素解法**（先看这个，复杂度如实写清，允许超时）→ **优化解法**（提交用）→ **ACM 版**（完整可运行，自己读标准输入、自己建链表和树）
- **三个附录**：
  - 附录 A：228 句口诀速查（表格）
  - 附录 B：228 条易错点速查（表格）
  - 附录 C：ACM 模式输入输出模板 15 节，含 `ListNode` / `TreeNode` / 邻接表 / 带权图 / 并查集 / 拓扑排序的定义与建表，每节一段完整程序 + 样例输入输出

## 排版

正文宋体小四、1.5 倍行距、首行缩进两字符；章标题「第 X 章」居中 + 细线；节标题「1.1 题目名（难度）」，
右侧标 LeetCode 题号；页眉章名、页脚页码；目录两级；PDF 带书签。代码块是 VSCode Dark+ 风格
（深色底、行号、文件名标签、VSCode 官方 token 配色）。

## 为什么可信

- 全书 **609 组测试用例**（每题 2~3 组）来自题目官方示例。
- **228 题 × 2 段代码 × 4 种语言 = 1824 段代码**，全部做了机器校验：
  - 912 段 **ACM 程序**全部在真实编译器下编译，并在 609 组用例上逐个跑通（输出逐字比对）；
  - 912 段 **LeetCode 版**全部编译通过（g++ -std=c++17 -fsyntax-only、javac、go build、Python AST）。
- 校验脚本在 `tools/` 里，可以自己复跑。

## 目录结构

```
.
├── book/                      四本 PDF
│   ├── leetcode-228-python.pdf
│   ├── leetcode-228-cpp.pdf
│   ├── leetcode-228-java.pdf
│   └── leetcode-228-go.pdf
├── tex/                       四本 PDF 的 LaTeX 源码（XeLaTeX + ctex）
│   ├── book_python.tex
│   ├── book_cpp.tex
│   ├── book_java.tex
│   └── book_go.tex
├── data/
│   ├── index.json             228 题目录（题号、标题、难度、分类）
│   ├── chapters.json          28 类题型的说明与 Python 模板
│   ├── chapters_cpp.json      同上，C++
│   ├── chapters_java.json     同上，Java
│   ├── chapters_go.json       同上，Go
│   ├── acm_appendix_cpp.json  附录 C 的 15 个模板（C++/Java/Go 各一份）
│   ├── python/g01..g11.json   每题内容（题意/示例/口诀/思路/复杂度/易错/两套代码/用例；
│   │                          其中 code=朴素解、code_opt=优化解、acm=完整程序）
│   ├── cpp/g01..g11.json      C++ 版代码（暂为单解 + ACM，待同步朴素/优化）
│   ├── java/g01..g11.json     Java 版代码（同上）
│   └── go/g01..g11.json       Go 版代码（同上）
└── tools/
    ├── mktex.py               由 data/ 生成 .tex（含词法高亮，输出 VSCode 配色）
    ├── mkpdf.py               数据加载
    ├── chapters.py            题型说明源文件
    ├── acm_appendix.py        附录 C 的 15 个模板
    ├── acm_appendix_cpp.json  附录 C 模板的 C++/Java/Go 版本（与 data/ 同源）
    ├── verify_lang.py         校验入口（本地跑，或 BUILD_HOST 远程跑）
    └── verify.py              远程校验器（编译 + 跑用例）
```

## 自己重新生成

```bash
# 1. 生成 LaTeX（BOOK_LANG = python / cpp / java / go）
BOOK_LANG=cpp python3 tools/mktex.py        # 产出 tex/book_cpp.tex

# 2. 编译（需要 TeX Live，含 ctex / tcolorbox / titlesec 等，XeLaTeX 三遍）
cd tex && xelatex -interaction=nonstopmode book_cpp.tex   # ×3（目录/书签/引用）

# 3. 校验代码（本机装了 g++ / javac / go 就直接跑；否则用 BUILD_HOST 丢到别的机器上跑）
python3 tools/verify_lang.py cpp data/cpp/g01.json
BUILD_HOST=user@host python3 tools/verify_lang.py java data/java/g01.json   # 远程编译
python3 tools/verify_lang.py cpp --chapters data/chapters_cpp.json          # 只编译题型模板
python3 tools/verify_lang.py go  --appendix tools/acm_appendix_go.json      # 附录 C：编译 + 跑样例
```

`tools/mktex.py` 里改 `PREAMBLE` 可以调字号、行距、页边距；改 `COL` 字典可以换代码配色。

## 更新记录

- **v1.1（2026-11）**：Python 版改成「先朴素、再优化」结构——每题先给最直白的解法（二维 `dp[i][j]` 表、暴力枚举、递归等），再给能过题的优化解，`idea` 也改成「朴素想法 → 慢在哪 → 怎么优化 → 复杂度」的叙事。共 188 题补了朴素解法、147 题补了优化解法块，页数 406 → 482。
- C++ / Java / Go 三本仍是单解结构，后续按同样规范同步。

## 说明

- 题目版权归 LeetCode 所有；题单分类参考了 [代码随想录](https://github.com/youngyangyang04/leetcode-master)
  的刷题路线（只参考了题单与分类，正文题意、思路、代码均为本仓库自行撰写）。
- 本书面向面试速成，解法优先「好记、好写」，不追求最优复杂度；同一道题如果存在更优解法，会在思路里点一句。
- 欢迎提 Issue 指正错误。

## 许可

代码与文字采用 [MIT License](LICENSE)。

注：题目（problem statements）版权归 LeetCode 所有；题单分类参考了代码随想录的刷题路线，
正文题意、思路、代码均为本仓库自行撰写。
