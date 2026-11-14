# -*- coding: utf-8 -*-
"""校验四种语言的代码：编译每个 LeetCode 版、把每个 ACM 版跑一遍用例。

用法：
    python3 tools/verify_lang.py cpp  data/cpp/g01.json
    python3 tools/verify_lang.py java data/java/g01.json [更多文件...]
    python3 tools/verify_lang.py go   --chapters data/chapters_go.json        # 只编译
    python3 tools/verify_lang.py cpp  --appendix tools/acm_appendix_cpp.json  # 编译 + 跑样例

两种运行方式：
    * 本机已装 g++ / javac / go：直接本地跑（默认）。
    * 想丢到别的机器上编译：设环境变量 BUILD_HOST=user@host，脚本会把批处理目录 scp 过去、
      在远端执行 verify.py，再取回报告。
"""
import io, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TOOLS = os.path.join(ROOT, "tools")
HOST = os.environ.get("BUILD_HOST", "").strip()
REMOTE = os.environ.get("BUILD_DIR", "~/verify")


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", **kw)


def load_tests():
    tests = {}
    d = os.path.join(DATA, "python")
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            for it in json.load(io.open(os.path.join(d, f), encoding="utf-8")):
                tests[str(it["id"])] = [[t[0], t[1]] for t in it.get("tests", [])]
    return tests


def main():
    lang = sys.argv[1]
    files = sys.argv[2:]
    tests = load_tests()

    chapters_mode = "--chapters" in files
    appendix_mode = "--appendix" in files
    files = [f for f in files if f not in ("--chapters", "--appendix")]

    manifest = []
    if chapters_mode:
        for path in files:
            for key, code in json.load(io.open(path, encoding="utf-8")).items():
                manifest.append({"id": key, "lang": lang, "code": "", "acm": code,
                                 "tests": [], "compile_only": True})
    elif appendix_mode:
        sys.path.insert(0, TOOLS)
        import acm_appendix as ACM
        samples = {x["id"]: x["sample"] for x in ACM.SECTIONS}
        for path in files:
            for iid, code in json.load(io.open(path, encoding="utf-8")).items():
                body = samples[iid].split("输入：", 1)[1]
                inp, out = body.split("输出：", 1) if "输出：" in body else (body, "")
                manifest.append({"id": iid, "lang": lang, "code": "", "acm": code,
                                 "tests": [[inp.strip("\n"), out.strip("\n")]]})
    else:
        missing = []
        for path in files:
            for it in json.load(io.open(path, encoding="utf-8")):
                iid = str(it["id"])
                if iid not in tests:
                    missing.append(iid)
                    continue
                manifest.append({"id": iid, "lang": lang, "code": it.get("code", ""),
                                 "acm": it.get("acm", ""), "tests": tests[iid]})
        if missing:
            print("!! 未知 id（不在 data/python 里）：", missing[:10])

    batch = os.path.join(ROOT, ".verify", "vbatch_%s_%d" % (lang, os.getpid()))
    shutil.rmtree(batch, ignore_errors=True)
    os.makedirs(batch)
    json.dump(manifest, io.open(os.path.join(batch, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    shutil.copy(os.path.join(TOOLS, "verify.py"), os.path.join(batch, "verify.py"))

    if HOST:
        name = os.path.basename(batch)
        sh(["ssh", "-o", "BatchMode=yes", HOST, "mkdir -p %s" % REMOTE])
        r = sh(["scp", "-r", batch, HOST + ":" + REMOTE + "/"])
        if r.returncode != 0:
            print("scp 失败：", r.stderr[:300])
            return 1
        r = sh(["ssh", "-o", "BatchMode=yes", HOST,
                "cd %s/%s && python3 verify.py ." % (REMOTE, name)])
        print((r.stdout or "").strip())
        subprocess.run(["scp", "-o", "BatchMode=yes",
                        "%s:%s/%s/report.json" % (HOST, REMOTE, name),
                        os.path.join(batch, "report.json")], capture_output=True)
        sh(["ssh", "-o", "BatchMode=yes", HOST, "rm -rf %s/%s" % (REMOTE, name)])
    else:
        r = sh([sys.executable, "verify.py", "."], cwd=batch, timeout=3600)
        print((r.stdout or "").strip())
        if r.returncode != 0:
            print("stderr:", (r.stderr or "")[-600:])

    rep_path = os.path.join(batch, "report.json")
    bad = []
    if os.path.exists(rep_path):
        bad = [x for x in json.load(io.open(rep_path, encoding="utf-8")) if x["errors"]]
        print("\n%d/%d ok, %d failed" % (len(manifest) - len(bad), len(manifest), len(bad)))
        for x in bad[:12]:
            print(" -", x["id"], x["errors"][0][:200])
    shutil.rmtree(batch, ignore_errors=True)
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
