# -*- coding: utf-8 -*-
"""book.tex v3 —— 学位论文式排版（黑/白/灰，宋体正文，无花哨盒子）+ VSCode Dark+ 代码块。"""
import io, os, re, json, sys
from collections import OrderedDict, Counter

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(ROOT, "data")          # 数据目录
sys.path.insert(0, W)
import chapters as CHMOD
import acm_appendix as ACM
from mkpdf import load_all

CH = CHMOD.CH
ORDER_I = CHMOD.CHAPTER_ORDER_I
ORDER_II = CHMOD.CHAPTER_ORDER_II

LANGS = {
    "python": {"name": "Python", "ver": "Python 3", "lc": "solution.py", "acm": "main.py", "tpl": "template.py"},
    "cpp": {"name": "C++", "ver": "C++17", "lc": "solution.cpp", "acm": "main.cpp", "tpl": "template.cpp"},
    "java": {"name": "Java", "ver": "Java 11", "lc": "Solution.java", "acm": "Main.java", "tpl": "Template.java"},
    "go": {"name": "Go", "ver": "Go 1.22", "lc": "solution.go", "acm": "main.go", "tpl": "template.go"},
}
LANG = os.environ.get("BOOK_LANG", "python")
LF = LANGS[LANG]


def load_lang_code():
    """merge data/<lang>/gNN.json (id -> code/acm) into the python contents"""
    d = os.path.join(W, LANG)
    out = {}
    if LANG == "python" or not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            try:
                for it in json.load(io.open(os.path.join(d, f), encoding="utf-8")):
                    out[str(it["id"])] = it
            except Exception as e:                        # noqa: BLE001
                print("!! bad lang file", f, e)
    return out


def load_lang_appendix():
    """work/acm_appendix_<lang>.json: {"C.1": "<code>"} —— 附录 C 模板的其它语言版本"""
    d = os.path.join(W, "acm_appendix_%s.json" % LANG)
    if LANG == "python" or not os.path.exists(d):
        return {}
    return json.load(io.open(d, encoding="utf-8"))


def load_lang_chapters():
    """work/chapters_<lang>.json: {"1|哈希": "<code>"} for the ACM template of each chapter"""
    d = os.path.join(W, "chapters_%s.json" % LANG)
    if LANG == "python" or not os.path.exists(d):
        return {}
    return json.load(io.open(d, encoding="utf-8"))

# ------------------------------------------------------------------ text escape
SUP = {"²": "$^{2}$", "³": "$^{3}$", "⁴": "$^{4}$"}
MATH = {"→": r"$\rightarrow$", "≤": r"$\leq$", "≥": r"$\geq$", "±": r"$\pm$",
        "×": r"$\times$", "√": r"$\surd$", "α": r"$\alpha$", "Ⅳ": "IV"}


def esc(s):
    out = []
    for ch in str(s or ""):
        if ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch in "&%$#_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        elif ch in SUP:
            out.append(SUP[ch])
        elif ch in MATH:
            out.append(MATH[ch])
        else:
            out.append(ch)
    return "".join(out)


# ------------------------------------------------------------------ code highlighter (VSCode Dark+)
KW_CTRL = {"if", "elif", "else", "for", "while", "return", "in", "not", "and", "or", "is",
           "break", "continue", "pass", "try", "except", "finally", "raise", "with", "as",
           "lambda", "yield", "assert", "global", "nonlocal", "del", "await", "async",
           "import", "from"}
KW_DEF = {"def", "class"}
KW_CONST = {"True", "False", "None", "self", "cls"}
CALLABLE = set("""len range print int str list dict set tuple sum max min abs sorted enumerate zip map
filter any all isinstance type ord chr bool float reversed divmod bytes deque heapq ListNode TreeNode
defaultdict Counter setdefault append extend pop popleft appendleft heappush heappop""".split())
METH_ATTR = {"next", "val", "left", "right", "append", "pop", "setdefault", "popleft", "heappush",
             "heappop", "sort", "join", "split", "strip", "items", "keys", "values", "get"}

TOK = re.compile(
    r"(?P<cmt>#[^\n]*)"
    r"|(?P<str>[fFrRbB]{0,2}(?:\"\"\"[\s\S]*?\"\"\"|'''[\s\S]*?'''|\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*'))"
    r"|(?P<num>\b\d+(?:\.\d+)?\b)"
    r"|(?P<name>[A-Za-z_][A-Za-z_0-9]*)"
    r"|(?P<op>->|==|!=|<=|>=|//|\*\*|[-+*/%<>=:,.;()[\]{}|&^~@])"
)

COL = {
    "kw": "vskw", "ctrl": "vsctrl", "const": "vskw", "func": "vsfunc", "class": "vsclass",
    "var": "vsvar", "num": "vsnum", "str": "vsstr", "cmt": "vscmt", "op": "vstext", "text": "vstext",
}


def esc_break(s):
    """escaped text with break points after commas / brackets, for long examples"""
    t = esc(s)
    for ch in (",", "]", ")", "}", "、", "，", "；"):
        t = t.replace(ch, ch + r"\allowbreak{}")
    return t


def _tok_line(line):
    """yield (text, colorkey) pieces for one code line"""
    out = []
    prev_colon = False
    i = 0
    tokens = list(TOK.finditer(line))
    # decide def/class names
    defname_next = False
    classname_next = False
    for m in tokens:
        text = m.group(0)
        gap = line[i:m.start()]
        if gap:
            out.append((gap, "text"))
        i = m.end()
        if m.group("cmt"):
            out.append((text, "cmt"))
            # rest of line is comment
            rest = line[i:]
            if rest:
                out.append((rest, "cmt"))
            i = len(line)
            break
        elif m.group("str"):
            out.append((text, "str"))
        elif m.group("num"):
            out.append((text, "num"))
        elif m.group("name"):
            if defname_next:
                out.append((text, "func"))
                defname_next = False
            elif classname_next:
                out.append((text, "class"))
                classname_next = False
            elif text in KW_DEF:
                out.append((text, "kw"))
                defname_next = text == "def"
                classname_next = text == "class"
            elif text in KW_CTRL:
                out.append((text, "ctrl"))
            elif text in KW_CONST:
                out.append((text, "const"))
            else:
                # attribute / call / plain
                before = line[:m.start()].rstrip()
                after = line[m.end():].lstrip()
                if before.endswith("."):
                    out.append((text, "var" if text in METH_ATTR else "func"))
                elif after.startswith("(") or text in CALLABLE:
                    out.append((text, "func"))
                else:
                    out.append((text, "text"))
        else:
            out.append((text, "op"))
    if i < len(line):
        out.append((line[i:], "text"))
    return out


def _emit_line(line):
    """LaTeX for one code line; spaces become \\hspace* so they survive exactly."""
    stripped = line.lstrip(" ")
    indent = len(line) - len(stripped)
    out = []
    for text, key in _tok_line(stripped):
        for piece in re.split(r"( +)", text):
            if not piece:
                continue
            if piece[0] == " ":
                out.append(r"\hspace*{%.2fem}\allowbreak{}" % (len(piece) * 0.602))
            else:
                out.append(r"\textcolor{%s}{%s}" % (COL[key], esc(piece)))
    return indent, "".join(out)


def code_tex(src, fname, lang=None):
    lang = lang or LF["name"]
    lines = (src or "").rstrip("\n").replace("\t", "    ").split("\n")
    o = [r"\begin{vscode}{%s}{%s}" % (esc(fname), esc(lang))]
    for n, line in enumerate(lines, 1):
        indent, body = _emit_line(line)
        o.append(r"\vsline{%d}{%.2fem}{%s}" % (n, indent * 0.602, body))
    o.append(r"\end{vscode}")
    return "\n".join(o)


# ------------------------------------------------------------------ preamble
PREAMBLE = r"""
\documentclass[12pt,openany,oneside,UTF8]{ctexbook}
\usepackage[a4paper,left=3.0cm,right=2.6cm,top=2.6cm,bottom=2.6cm,
  headheight=23pt,headsep=9pt,footskip=16pt]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{titletoc}
\usepackage{fancyhdr}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{needspace}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}
\usepackage[hidelinks,bookmarksnumbered,bookmarksopen]{hyperref}
\hypersetup{pdftitle={LeetCode 刷题速成手册},pdfauthor={Hot100 + 代码随想录}}

% ---------- 字体：宋体正文 / 黑体标题 / 楷体口诀
\setCJKmainfont{Noto Serif CJK SC}[BoldFont={Noto Serif CJK SC},BoldFeatures={FakeBold=2.0}]
\setCJKsansfont{Noto Sans CJK SC}[BoldFont={Noto Sans CJK SC},BoldFeatures={FakeBold=1.2}]
\setCJKmonofont{Noto Sans CJK SC}
\setCJKfamilyfont{zhkai}{FandolKai-Regular.otf}
\newcommand{\kai}{\CJKfamily{zhkai}}
\setmainfont{Noto Serif CJK SC}
\setsansfont{Noto Sans CJK SC}
\setmonofont{DejaVu Sans Mono}[Scale=0.88]

% ---------- 版式：1.5 倍行距，首行缩进 2 字符
\linespread{1.5}
\setlength{\parindent}{2em}
\setlength{\parskip}{0pt}
\setlength{\emergencystretch}{3em}

% ---------- VSCode Dark+ 配色
\definecolor{vcbg}{HTML}{1E1E1E}
\definecolor{vctab}{HTML}{252526}
\definecolor{vctabfg}{HTML}{CFCFCF}
\definecolor{vstext}{HTML}{D4D4D4}
\definecolor{vskw}{HTML}{569CD6}
\definecolor{vsctrl}{HTML}{C586C0}
\definecolor{vsfunc}{HTML}{DCDCAA}
\definecolor{vsclass}{HTML}{4EC9B0}
\definecolor{vsvar}{HTML}{9CDCFE}
\definecolor{vsnum}{HTML}{B5CEA8}
\definecolor{vsstr}{HTML}{CE9178}
\definecolor{vscmt}{HTML}{6A9955}
\definecolor{vsgutter}{HTML}{858585}
\definecolor{ink}{HTML}{1A1A1A}
\definecolor{grayt}{HTML}{595959}
\definecolor{ruleg}{HTML}{BFBFBF}

\renewcommand{\thechapter}{第\,\arabic{chapter}\,章}
\renewcommand{\thesection}{\arabic{chapter}.\arabic{section}}

% ---------- 章标题（居中，第 X 章 + 标题 + 细线）
\titleformat{\chapter}[display]
  {\normalfont\sffamily\centering}
  {\fontsize{14}{18}\selectfont \thechapter}
  {10pt}
  {\fontsize{18}{24}\selectfont\bfseries}
  [\vspace{6pt}{\color{ruleg}\rule{\linewidth}{0.6pt}}\vspace{2pt}]
\titlespacing*{\chapter}{0pt}{-6pt}{22pt}

% ---------- 节标题（1.1 题目名，左对齐）
\titleformat{\section}[hang]
  {\normalfont\sffamily\bfseries\fontsize{13.5}{17}\selectfont}
  {\thesection}{0.8em}{}
\titlespacing*{\section}{0pt}{20pt}{6pt}

% ---------- 页眉页脚：页眉章名 + 细线，页脚页码
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{ruleg}\leaders\hrule height \headrulewidth\hfill}}
\fancyhead[C]{\normalfont\fontsize{9}{11}\selectfont\color{grayt}\leftmark}
\fancyfoot[C]{\normalfont\fontsize{10}{12}\selectfont\color{grayt}\thepage}
\renewcommand{\chaptermark}[1]{\markboth{\thechapter\quad #1}{}}
\fancypagestyle{plain}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}%
  \fancyfoot[C]{\normalfont\fontsize{10}{12}\selectfont\color{grayt}\thepage}}

% ---------- 目录
\renewcommand{\contentsname}{目\quad 录}
\titlecontents{chapter}[0pt]{\addvspace{9pt}\sffamily\bfseries\fontsize{11}{14}\selectfont}
  {\contentslabel{5.6em}}{}{\hfill\contentspage}[\addvspace{2pt}]
\titlecontents{section}[2.4em]{\addvspace{1pt}\fontsize{10.5}{13.5}\selectfont}
  {\contentslabel{3.4em}}{}{\titlerule*[0.6pc]{.}\;\contentspage}

% ---------- VSCode 代码块
\newtcolorbox{vscode}[2]{enhanced, breakable,
  colback=vcbg, colframe=vcbg, boxrule=0pt, arc=1.6mm, auto outer arc,
  left=7pt, right=7pt, top=0pt, bottom=6pt,
  colbacktitle=vctab, coltitle=vctabfg, fonttitle=\ttfamily\fontsize{7.4}{9}\selectfont,
  fontupper=\ttfamily\fontsize{7.7}{10.1}\selectfont\linespread{1}\selectfont,
  title={#1\quad{\color{vsgutter}|}\quad #2}, halign title=left,
  toptitle=3.4pt, bottomtitle=3.4pt, titlerule=0pt,
  before skip=9pt, after skip=11pt}
\newtcolorbox{iobox}{enhanced, breakable, colback=white, colframe=black!28, boxrule=0.4pt,
  arc=0pt, left=8pt, right=8pt, top=5pt, bottom=5pt, before skip=5pt, after skip=7pt,
  fontupper=\raggedright}
\newcommand{\vsline}[3]{\par\noindent\vspace{0pt}%
  \makebox[2.0em][r]{\color{vsgutter}\fontsize{6.4}{7.8}\selectfont #1}%
  \hspace{0.55em}\hspace*{#2}{\color{vstext}\vphantom{Ag}#3}\par}

% ---------- 正文小工具
\newcommand{\lab}[1]{\textbf{#1}\hspace{0.5em}}
\newcommand{\bodyfont}{\fontsize{12}{18}\selectfont}
\newcommand{\smallfont}{\fontsize{10.5}{15}\selectfont}
\setlength{\skip\footins}{12pt}
\newcommand{\tablefont}{\fontsize{10}{13}\selectfont\linespread{1.08}\selectfont\renewcommand{\arraystretch}{1.22}}
\newcommand{\appchapter}[1]{%
  \clearpage
  \phantomsection
  \addcontentsline{toc}{chapter}{\protect\numberline{}#1}%
  \markboth{#1}{#1}%
  \begin{center}
  {\sffamily\bfseries\fontsize{18}{24}\selectfont #1\par}
  \vspace{5pt}
  {\color{ruleg}\rule{\linewidth}{0.6pt}}
  \end{center}
  \vspace{16pt}}
\begin{document}
\pagestyle{empty}
"""

COVER = r"""
\begin{titlepage}
\thispagestyle{empty}
\centering
\vspace*{3.2cm}
{\sffamily\bfseries\fontsize{26}{32}\selectfont LeetCode 刷题速成手册\par}
\vspace{0.9cm}
{\sffamily\fontsize{15}{20}\selectfont 热题 100 与代码随想录题单\par}
\vspace{0.35cm}
{\sffamily\fontsize{12}{17}\selectfont 228 道高频题 · Python 题解 · ACM 模式程序\par}
\vspace{1.4cm}
{\color{ruleg}\rule{11cm}{0.6pt}\par}
\vspace{1.2cm}
{\fontsize{12}{20}\selectfont
\begin{tabular}{r@{\quad}l}
速成篇 & Hot 100 全量 100 题，17 类题型 \\[3pt]
补充篇 & 代码随想录题单 128 题，11 个专题 \\[3pt]
每题 & 题意 · 示例 · 一句话记忆 · 思路 · 复杂度 · 易错 \\[3pt]
代码 & LeetCode 提交版 + ACM 模式完整程序（Python 3） \\
\end{tabular}\par}
\vfill
{\sffamily\fontsize{12}{16}\selectfont 2026 年 11 月\par}
\vspace{0.5cm}
\end{titlepage}
"""


def part_page(tag, title, blurb, bullets):
    return "\n".join([
        r"\clearpage", r"\thispagestyle{empty}",
        r"\phantomsection\addcontentsline{toc}{chapter}{\protect\numberline{}%s}" % esc("%s　%s" % (tag, title)),
        r"\markboth{%s}{%s}" % (esc("%s　%s" % (tag, title)), esc("%s　%s" % (tag, title))),
        r"\vspace*{4.2cm}",
        r"\begin{center}",
        r"{\sffamily\fontsize{13}{18}\selectfont\color{grayt}%s\par}" % esc(tag),
        r"\vspace{0.6cm}",
        r"{\sffamily\bfseries\fontsize{22}{28}\selectfont %s\par}" % esc(title),
        r"\vspace{0.7cm}",
        r"{\color{ruleg}\rule{10cm}{0.6pt}\par}",
        r"\vspace{0.7cm}",
        r"\begin{minipage}{11.5cm}\raggedright\fontsize{11}{19}\selectfont\color{grayt}",
        esc(blurb) + r"\par\vspace{8pt}",
        r"\begin{itemize}[leftmargin=1.2em,itemsep=4pt,label={\color{grayt}--}]",
        "\n".join(r"\item " + esc(x) for x in bullets),
        r"\end{itemize}",
        r"\end{minipage}",
        r"\end{center}",
        r"\vfill",
    ])


def howto():
    t = [r"\clearpage", r"\pagenumbering{arabic}", r"\pagestyle{fancy}",
         r"\phantomsection\addcontentsline{toc}{chapter}{\protect\numberline{}前言：怎么用这本书}",
         r"\markboth{前言：怎么用这本书}{前言：怎么用这本书}",
         r"\chapter*{前\quad 言}", r"\markboth{前\quad 言}{前\quad 言}",
         r"\vspace{-0.6cm}",
         r"{\bodyfont",
         r"\hspace*{2em}这是一本给「赶时间」的人用的刷题手册：从力扣「热题 100」的 100 道题，到代码随想录题单里热题 100 之外的 128 道题，"
         r"共 228 题，每题只保留最需要记的东西——一句话口诀、思路要点、复杂度、易错点，以及两套可直接使用的 {LANGNAME} 代码。\par",
         r"\par\hspace*{2em}与常见的题解书不同，本书不追求讲透每一道题的来龙去脉，而是按「面试验证」的方式组织：能不能在一分钟内说清思路，"
         r"能不能在十分钟内写对代码。因此每道题都先给一句能背下来的口诀，再给 3 到 6 条能直接当答案说的要点，最后才给代码。\par",
         r"}"]

    items = [
        ("一句话记忆", "每题都有一句口语化的口诀。考前只翻附录 A，四十分钟就能把 228 道题的思路过一遍——这是性价比最高的一轮复习。"),
        ("思路要点", "3 到 6 条，顺序就是面试口述的顺序：先一句核心思想，再两三句实现细节（状态定义、指针移动、转移方程），最后一句边界。"),
        ("LeetCode 版", "函数签名与力扣一致，可直接粘贴提交；链表、二叉树的节点定义沿用官方写法，不必自己建表。"),
        ("ACM 版", "笔试常考 ACM 模式：没有 Solution 类，要自己读标准输入、自己建链表和树、自己输出。每题都给了完整可运行的程序。"),
        ("题型模板", "每一章开头的一节说明这一类题在 ACM 模式下怎么读入、怎么输出，并给出模板程序，改两行就能用。"),
    ]
    t.append(r"\vspace{6pt}\noindent{\sffamily\bfseries\fontsize{13}{17}\selectfont 一、本书的结构}\par\vspace{4pt}")
    t.append(r"\begin{enumerate}[leftmargin=2.2em,itemsep=5pt,topsep=2pt,label={\bfseries\arabic*.}]")
    for k, v in items:
        t.append(r"\item {\bodyfont \textbf{%s}　%s\par}" % (esc(k), esc(v)))
    t.append(r"\end{enumerate}")

    t.append(r"\vspace{10pt}\noindent{\sffamily\bfseries\fontsize{13}{17}\selectfont 二、七天速成计划}\par\vspace{5pt}")
    plan = [("第 1 天", "哈希、双指针、滑动窗口、子串、普通数组、矩阵（21 题）", "把数组上的几套固定套路打熟"),
            ("第 2 天", "链表（14 题）", "哨兵节点与快慢指针，手写不出错"),
            ("第 3 天", "二叉树（15 题）", "递归三部曲：参数、终止、单层逻辑"),
            ("第 4 天", "图论、回溯、二分查找（18 题）", "网格 DFS、回溯去重、二分边界"),
            ("第 5 天", "栈、堆、贪心（12 题）", "单调栈、堆取 TopK、区间贪心"),
            ("第 6 天", "动态规划、多维动态规划（15 题）", "背包五步法，滚动数组方向不能写反"),
            ("第 7 天", "技巧（5 题）＋ 附录 A 全过一遍 ＋ 补充篇错题", "查漏补缺，稳定输出")]
    t.append(r"{\tablefont\setlength{\tabcolsep}{3pt}")
    t.append(r"\begin{longtable}{@{}>{\leavevmode\raggedright\arraybackslash}p{1.9cm}"
             r">{\leavevmode\raggedright\arraybackslash}p{8.6cm}"
             r">{\leavevmode\raggedright\arraybackslash}p{4.4cm}@{}}")
    t.append(r"\toprule")
    t.append(r"\textbf{天} & \textbf{内容} & \textbf{目标}\\ \midrule")
    t.append(r"\endhead")
    for a, b, c in plan:
        t.append(r"%s & %s & %s\\" % (esc(a), esc(b), esc(c)))
    t.append(r"\bottomrule")
    t.append(r"\end{longtable}}")

    t.append(r"\vspace{12pt}\indent{\bodyfont "
             r"\textbf{三遍法}：第一遍只看题意和一句话记忆，能复述就过；第二遍合上书手写 LeetCode 版，写不出来再看代码；"
             r"第三遍只看 ACM 版，专门练输入输出。三遍下来，228 题足以覆盖绝大多数笔试和一面。\par}")
    t.append(r"\indent{\bodyfont "
             r"\textbf{关于补充篇}：热题 100 已经覆盖了高频考点，但代码随想录的题更偏体系——背包、单调栈、并查集、拓扑排序、"
             r"最短路径这些在笔试里经常以变体出现，建议按专题顺序补。\par}")
    return "\n".join(t)


def chapter(part, cat, ci, probs, contents):
    num = "I-%d" % ci if part == 1 else "II-%d" % ci
    cnt = Counter((contents.get(str(p["id"])) or {}).get("diff") or "中等" for p in probs)
    diff_txt = "，".join("%s %d" % (k, cnt[k]) for k in ("简单", "中等", "困难") if cnt[k])
    o = [r"\clearpage",
         r"\chapter{%s}" % esc(cat),
         r"\begin{flushleft}",
         r"{\smallfont\color{grayt}%s　%d 题（%s）\par}" % (esc(num), len(probs), esc(diff_txt)),
         r"\end{flushleft}",
         r"\vspace{2pt}"]
    ch = CH.get("%d|%s" % (part, cat)) or {}
    o.append(r"\noindent{\sffamily\bfseries\fontsize{12.5}{16}\selectfont 这一类输入怎么读}\par\vspace{3pt}")
    o.append(r"\indent{\bodyfont %s\par}" % esc((ch.get("lead", "") or "").replace("`", "")))
    o.append(r"\vspace{4pt}")
    tpl = load_lang_chapters().get("%d|%s" % (part, cat)) or ch.get("code", "")
    o.append(code_tex(tpl, LF["tpl"]))
    o.append(r"\noindent{\bodyfont\textbf{输出注意}　%s\par}" % esc((ch.get("out", "") or "").replace("`", "")))
    o.append(r"\vspace{6pt}")
    o.append(r"\noindent{\smallfont\textbf{本章题单}　%s\par}"
             % "，".join("%s %s" % (esc(p["num"]) if p["num"] else "剑指", esc(p["title"])) for p in probs))
    o.append(r"\vspace{4pt}")
    for p in probs:
        o.append(problem(p, contents))
    return "\n".join(o)


def problem(p, contents):
    d = contents.get(str(p["id"])) or {}
    num = str(p["num"]) if p["num"] else "剑指 Offer"
    name = p["title"]
    diff = d.get("diff") or "中等"
    o = [r"\vspace{2pt}",
         r"\section[%s]{%s（%s）\hfill{\normalfont\fontsize{9.5}{12}\selectfont\color{grayt}%s}}"
         % (esc(name), esc(name), esc(diff), esc("LeetCode " + num if p["num"] else "剑指 Offer")),
         r"\indent{\bodyfont \lab{题意}%s\par}" % esc(d.get("stmt", "")),
         r"\vspace{5pt}",
         r"\noindent{\lab{示例}\begingroup\raggedright"
         r"\fontsize{9.6}{13}\selectfont\ttfamily %s\par\endgroup}" % esc_break(d.get("ex", "")),
         r"\vspace{9pt}",
         r"\noindent{\bodyfont \lab{记忆}\quad{\kai %s}\par}" % esc(d.get("key", "")),
         r"\vspace{11pt}",
         r"\noindent{\sffamily\bfseries\fontsize{11.5}{15}\selectfont 思路}\par\vspace{3pt}",
         r"\begin{enumerate}[leftmargin=2.0em,itemsep=4pt,topsep=1pt,parsep=0pt,"
         r"label={\fontsize{10.5}{13}\selectfont\arabic*.}]"]
    for it in d.get("idea", []):
        o.append(r"\item {\smallfont %s\par}" % esc(it))
    o.append(r"\end{enumerate}")
    o.append(r"\vspace{6pt}\noindent{\bodyfont \lab{复杂度}%s\par}" % esc(d.get("cx", "")))
    o.append(r"\vspace{4pt}\noindent{\bodyfont \lab{易错}%s\par}" % esc(d.get("trap", "")))
    o.append(r"\vspace{13pt}")
    o.append(r"\noindent{\smallfont\sffamily\bfseries LeetCode 版（可直接提交）}\par\vspace{-5pt}")
    o.append(code_tex(d.get("code", ""), LF["lc"]))
    o.append(r"\noindent{\smallfont\sffamily\bfseries ACM 版（完整可运行）}\par\vspace{-5pt}")
    o.append(code_tex(d.get("acm", ""), LF["acm"]))
    return "\n".join(o)


def appendix(idx, contents):
    o = [r"\appchapter{附录 A\quad 228 句口诀速查}",
         r"\indent{\bodyfont 考前四十分钟把下表刷一遍，能复述就打勾。\par}\vspace{8pt}"]
    rows = []
    for order, key in ((ORDER_I, "hot"), (ORDER_II, "extras")):
        bycat = OrderedDict()
        for it in idx[key]:
            bycat.setdefault(it["cat"], []).append(it)
        for cat in order:
            for p in bycat.get(cat) or []:
                d = contents.get(str(p["id"])) or {}
                rows.append((str(p["num"]) if p["num"] else "剑指", p["title"], d.get("key", "")))
    o.append(r"{\tablefont\setlength{\tabcolsep}{5pt}")
    o.append(r"\begin{longtable}{@{}>{\leavevmode\raggedleft\arraybackslash}p{1.4cm}"
             r">{\leavevmode\raggedright\arraybackslash}p{4.4cm}"
             r">{\leavevmode\raggedright\arraybackslash}p{8.3cm}@{}}")
    o.append(r"\toprule")
    o.append(r"\textbf{题号} & \textbf{题目} & \textbf{一句话口诀}\\ \midrule")
    o.append(r"\endhead")
    for n, t, k in rows:
        o.append(r"%s & %s & %s\\" % (esc(n), esc(t), esc(k)))
    o.append(r"\bottomrule")
    o.append(r"\end{longtable}}")

    o += [r"\appchapter{附录 B\quad 易错点速查}",
          r"\indent{\bodyfont 按章节顺序排列，做题前扫一眼。\par}\vspace{8pt}"]
    rows2 = []
    for order, key in ((ORDER_I, "hot"), (ORDER_II, "extras")):
        bycat = OrderedDict()
        for it in idx[key]:
            bycat.setdefault(it["cat"], []).append(it)
        for cat in order:
            for p in bycat.get(cat) or []:
                d = contents.get(str(p["id"])) or {}
                rows2.append((p["title"], d.get("trap", "")))
    o.append(r"{\tablefont\setlength{\tabcolsep}{3pt}")
    o.append(r"\begin{longtable}{@{}>{\leavevmode\raggedright\arraybackslash}p{4.8cm}"
             r">{\leavevmode\raggedright\arraybackslash}p{9.9cm}@{}}")
    o.append(r"\toprule")
    o.append(r"\textbf{题目} & \textbf{易错点}\\ \midrule")
    o.append(r"\endhead")
    for t, k in rows2:
        o.append(r"%s & %s\\" % (esc(t), esc(k)))
    o.append(r"\bottomrule")
    o.append(r"\end{longtable}}")
    return "\n".join(o)


def io_box(sample):
    """render an "输入 / 输出" sample inside a thin framed box"""
    body = sample.split("输入：", 1)[1]
    if "输出：" in body:
        inp, out = body.split("输出：", 1)
    else:
        inp, out = body, ""

    def lines(t):
        rows = [x for x in t.strip("\n").split("\n") if x.strip() != ""]
        return r"\\".join(esc(x) for x in rows)

    o = [r"\begin{iobox}",
         r"{\sffamily\bfseries\smallfont 输入}\par\vspace{2pt}",
         r"{\ttfamily\smallfont %s}\par" % lines(inp)]
    if out.strip():
        o += [r"\vspace{5pt}",
              r"{\sffamily\bfseries\smallfont 输出}\par\vspace{2pt}",
              r"{\ttfamily\smallfont %s}\par" % lines(out)]
    o.append(r"\end{iobox}")
    return "\n".join(o)


def appendix_c():
    APPX = load_lang_appendix()
    o = [r"\appchapter{附录 C\quad ACM 模式输入输出模板}",
         r"\indent{\bodyfont 这一节收录笔试里最常见的十五种输入形态，每一种都给一段完整可运行的"
         r"程序：上面是题目给的输入和应有的输出，中间是读入 + 计算 + 输出的全流程。抄的时候只改中间"
         r"计算那几行即可。\par}",
         r"\vspace{6pt}"]
    for s in ACM.SECTIONS:
        o.append(r"\vspace{14pt}")
        o.append(r"\phantomsection\addcontentsline{toc}{section}{%s\quad %s}"
                 % (esc(s["id"]), esc(s["title"])))
        o.append(r"{\sffamily\bfseries\fontsize{12.5}{16}\selectfont %s\quad %s}\par"
                 % (esc(s["id"]), esc(s["title"])))
        o.append(r"\vspace{6pt}")
        o.append(r"\indent{\bodyfont %s\par}" % esc(s["intro"]))
        o.append(r"\vspace{3pt}")
        o.append(io_box(s["sample"]))
        code = APPX.get(s["id"], s["code"])
        o.append(code_tex(code, LF["tpl"]))
        o.append(r"\noindent{\bodyfont \lab{注意}%s\par}" % esc(s["note"]))
    return "\n".join(o)


def main():
    idx, contents, hot, ext = load_all()
    lang_code = load_lang_code()
    for k, v in contents.items():
        if k in lang_code:
            v["code"] = lang_code[k].get("code", v.get("code", ""))
            v["acm"] = lang_code[k].get("acm", v.get("acm", ""))
    parts = [PREAMBLE, COVER, howto(),
             r"\clearpage",
             r"\markboth{目\quad 录}{目\quad 录}",
             r"\tableofcontents"]

    parts.append(part_page("第一篇", "Hot 100 速成篇",
                           "力扣热题 100 全量 100 题，按 17 类题型组织：先背一句话，再手写一遍代码。",
                           ["每题：一句话记忆、题意、示例、思路要点、复杂度、易错点",
                            "两套代码：LeetCode 提交版与 ACM 模式完整可运行版",
                            "每章开头：这一类输入在 ACM 模式下怎么读、怎么输出"]))
    for ci, cat in enumerate(ORDER_I, 1):
        probs = hot.get(cat) or []
        if probs:
            parts.append(chapter(1, cat, ci, probs, contents))

    parts.append(part_page("第二篇", "代码随想录补充篇",
                           "热题 100 之外，代码随想录题单里的 128 道 LeetCode 题，按 11 个专题补齐知识体系。",
                           ["数组、链表、哈希表、字符串、栈与队列、单调栈",
                            "二叉树 22 题，回溯 10 题，贪心 13 题",
                            "动态规划 26 题，图论 18 题",
                            "同样每题配 LeetCode 版与 ACM 版代码"]))
    for ci, cat in enumerate(ORDER_II, 1):
        probs = ext.get(cat) or []
        if probs:
            parts.append(chapter(2, cat, ci, probs, contents))

    parts.append(appendix(idx, contents))
    parts.append(appendix_c())
    parts.append(r"\end{document}")
    tex = "\n".join(parts)
    tex = tex.replace("Python 题解 · ACM 模式程序", "%s 题解 · ACM 模式程序" % LF["name"])
    tex = tex.replace("Python 3）", "%s）" % LF["ver"])
    tex = tex.replace("{LANGNAME}", LF["name"])
    path = os.path.join(ROOT, "tex", "book_%s.tex" % LANG)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(tex)
    n = sum(1 for p in tex.split("\n") if p.startswith(r"\section["))
    print("problems:", n, "size:", len(tex) // 1024, "KB ->", path)


if __name__ == "__main__":
    main()
