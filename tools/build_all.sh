#!/usr/bin/env bash
# 依次生成四个语言的 LaTeX 并用 XeLaTeX 编译三遍
set -e
cd "$(dirname "$0")/.."
for lang in python cpp java go; do
  echo "== $lang"
  BOOK_LANG=$lang python3 tools/mktex.py
  (cd tex && xelatex -interaction=nonstopmode book_$lang.tex >/dev/null 2>&1 || true
   xelatex -interaction=nonstopmode book_$lang.tex >/dev/null 2>&1 || true
   xelatex -interaction=nonstopmode book_$lang.tex >/dev/null 2>&1 || true)
  cp "tex/book_$lang.pdf" "book/leetcode-228-$lang.pdf"
done
echo done
