# -*- coding: utf-8 -*-
"""Server-side verifier: compile every snippet and run every ACM program against its tests.

usage: python3 verify.py <batch-dir>
batch-dir contains manifest.json: [{"id","lang","code","acm","tests":[[in,out],...]}]
prints a JSON report on stdout (last line) and a human summary on stderr.
"""
import json, os, re, shutil, subprocess, sys, tempfile, time

TIMEOUT = 30


def norm(s):
    lines = [ln.rstrip() for ln in (s or "").replace("\r\n", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def sh(cmd, cwd, stdin=None, timeout=TIMEOUT):
    try:
        return subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def err_tail(r, n=3):
    txt = (r.stderr or "") + (r.stdout or "")
    lines = [ln for ln in txt.strip().split("\n") if ln.strip()]
    return " | ".join(lines[:n])[:320]


# ---------------------------------------------------------------- C++
def check_cpp(item, work):
    errs = []
    code, acm, tests = item["code"], item["acm"], item["tests"]
    if not item.get("compile_only"):
        src = code if "#include" in code[:400] else "#include <bits/stdc++.h>\nusing namespace std;\n\n" + code
        p = os.path.join(work, "sol.cpp")
        open(p, "w", encoding="utf-8").write(src)
        r = sh(["g++", "-std=c++17", "-O1", "-fsyntax-only", "sol.cpp"], work)
        if r is None:
            errs.append("code: compile timeout")
        elif r.returncode != 0:
            errs.append("code: " + err_tail(r))
    # 2) ACM program: build + run
    p2 = os.path.join(work, "main.cpp")
    open(p2, "w", encoding="utf-8").write(acm)
    r = sh(["g++", "-std=c++17", "-O2", "-o", "main", "main.cpp"], work, timeout=60)
    if r is None or r.returncode != 0:
        errs.append("acm: " + (("compile timeout") if r is None else err_tail(r)))
        return errs
    for i, (inp, want) in enumerate(tests):
        r = sh(["./main"], work, stdin=inp + "\n")
        if r is None:
            errs.append(f"test{i}: timeout")
        elif r.returncode != 0:
            errs.append(f"test{i}: rc={r.returncode} {err_tail(r, 1)}")
        elif norm(r.stdout) != norm(want):
            errs.append(f"test{i}: got {norm(r.stdout)[:90]!r} want {norm(want)[:90]!r}")
    return errs


# ---------------------------------------------------------------- Java
def java_class_name(code):
    m = re.search(r"public\s+(?:final\s+|abstract\s+)?class\s+(\w+)", code)
    return m.group(1) if m else ("Solution" if "class Solution" in code else "Main")


def check_java(item, work):
    errs = []
    code, acm, tests = item["code"], item["acm"], item["tests"]
    if not item.get("compile_only"):
        name = java_class_name(code)
        p = os.path.join(work, name + ".java")
        open(p, "w", encoding="utf-8").write(code)
        r = sh(["javac", "-encoding", "UTF-8", "-nowarn", name + ".java"], work, timeout=60)
        if r is None:
            errs.append("code: compile timeout")
        elif r.returncode != 0:
            errs.append("code: " + err_tail(r))

    p2 = os.path.join(work, "Main.java")
    open(p2, "w", encoding="utf-8").write(acm)
    r = sh(["javac", "-encoding", "UTF-8", "-nowarn", "Main.java"], work, timeout=60)
    if r is None or r.returncode != 0:
        errs.append("acm: " + (("compile timeout") if r is None else err_tail(r)))
        return errs
    for i, (inp, want) in enumerate(tests):
        r = sh(["java", "-Xss64m", "-Dfile.encoding=UTF-8", "Main"], work, stdin=inp + "\n")
        if r is None:
            errs.append(f"test{i}: timeout")
        elif r.returncode != 0:
            errs.append(f"test{i}: rc={r.returncode} {err_tail(r, 1)}")
        elif norm(r.stdout) != norm(want):
            errs.append(f"test{i}: got {norm(r.stdout)[:90]!r} want {norm(want)[:90]!r}")
    return errs


# ---------------------------------------------------------------- Go
def check_go(item, work):
    errs = []
    code, acm, tests = item["code"], item["acm"], item["tests"]
    if not item.get("compile_only"):
        p = os.path.join(work, "sol.go")
        open(p, "w", encoding="utf-8").write(
            "package main\n\n" + code + "\n\nfunc main() {}\n")
        r = sh(["go", "build", "-o", os.devnull, "sol.go"], work, timeout=60)
        if r is None:
            errs.append("code: compile timeout")
        elif r.returncode != 0:
            errs.append("code: " + err_tail(r, 4))
    # 2) ACM program
    p2 = os.path.join(work, "main.go")
    open(p2, "w", encoding="utf-8").write(acm)
    r = sh(["go", "build", "-o", "prog", "main.go"], work, timeout=90)
    if r is None or r.returncode != 0:
        errs.append("acm: " + (("compile timeout") if r is None else err_tail(r, 4)))
        return errs
    for i, (inp, want) in enumerate(tests):
        r = sh(["./prog"], work, stdin=inp + "\n")
        if r is None:
            errs.append(f"test{i}: timeout")
        elif r.returncode != 0:
            errs.append(f"test{i}: rc={r.returncode} {err_tail(r, 1)}")
        elif norm(r.stdout) != norm(want):
            errs.append(f"test{i}: got {norm(r.stdout)[:90]!r} want {norm(want)[:90]!r}")
    return errs


CHECK = {"cpp": check_cpp, "java": check_java, "go": check_go}


def main():
    batch = sys.argv[1]
    items = json.load(open(os.path.join(batch, "manifest.json"), encoding="utf-8"))
    report = []
    for it in items:
        work = os.path.join(batch, "work", str(it["id"]))
        os.makedirs(work, exist_ok=True)
        t0 = time.time()
        try:
            errs = CHECK[it["lang"]](it, work)
        except Exception as e:                       # noqa: BLE001
            errs = ["verifier crash: %r" % (e,)]
        report.append({"id": it["id"], "lang": it["lang"], "errors": errs,
                       "sec": round(time.time() - t0, 1)})
        shutil.rmtree(work, ignore_errors=True)
    nbad = sum(1 for r in report if r["errors"])
    print("SUMMARY: %d/%d ok" % (len(report) - nbad, len(report)))
    for r in report:
        if r["errors"]:
            print("FAIL %s" % r["id"])
            for e in r["errors"][:4]:
                print("   ", e)
    json.dump(report, open(os.path.join(batch, "report.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("REPORT_WRITTEN")


if __name__ == "__main__":
    main()
