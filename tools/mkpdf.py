# -*- coding: utf-8 -*-
"""Lay out and render the whole book to PDF (no external tools: own text engine)."""
import io, os, re, json, sys, math
from collections import OrderedDict, Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\31964\Desktop\leetcode\work")
from pdfkit import PDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(ROOT, "data")          # data/index.json, data/chapters.json, data/<lang>/gNN.json
OUT = os.path.join(W, "python")
import chapters as CHMOD

CH = CHMOD.CH
ORDER_I = CHMOD.CHAPTER_ORDER_I
ORDER_II = CHMOD.CHAPTER_ORDER_II

# ---------------------------------------------------------------- geometry
PW, PH = 595.28, 841.89
ML, MR, MT, MB = 44, 44, 40, 46
CW = PW - ML - MR              # 507.28
FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"
MONO_PATH = r"C:\Windows\Fonts\consola.ttf"
MONO_B_PATH = r"C:\Windows\Fonts\consolab.ttf"

C = {
    "ink": (0.10, 0.12, 0.15),
    "ink2": (0.22, 0.26, 0.31),
    "gray": (0.42, 0.46, 0.52),
    "gray2": (0.55, 0.60, 0.66),
    "navy": (0.043, 0.13, 0.30),
    "blue": (0.145, 0.388, 0.87),
    "blue2": (0.11, 0.25, 0.53),
    "accent": (0.94, 0.71, 0.16),
    "white": (1, 1, 1),
    "rule": (0.84, 0.87, 0.91),
    "bg": (0.968, 0.976, 0.988),
    "keybg": (1.0, 0.984, 0.92),
    "keybr": (0.97, 0.84, 0.48),
    "keyink": (0.48, 0.29, 0.02),
    "trapbg": (1.0, 0.96, 0.945),
    "trapbr": (0.98, 0.45, 0.086),
    "trapink": (0.60, 0.20, 0.07),
    "easy": (0.086, 0.64, 0.29),
    "mid": (0.85, 0.47, 0.02),
    "hard": (0.86, 0.15, 0.15),
    "codebg": (0.968, 0.976, 0.988),
    "kw": (0.72, 0.11, 0.11),
    "str": (0.06, 0.48, 0.25),
    "num": (0.48, 0.23, 0.93),
    "cmt": (0.58, 0.64, 0.71),
    "bi": (0.11, 0.31, 0.85),
}
DIFF_COL = {"简单": "easy", "中等": "mid", "困难": "hard"}

# ---------------------------------------------------------------- text utils
CJK_RE = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f\u2010-\u201f\u2026\u00b7]")
CLOSE = set("，。、；：？！）】》」』”’,.;:?!)]}%‰℃…·")
OPEN = set("（【《「『“‘([{")


def wrap_runs(runs, maxw, fonts):
    """runs: list of (text, style dict). style keys: f(font key), sz, col, bold, mono.
    returns list of lines; line = list of (text, style)."""
    units = []
    for text, st in runs:
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if CJK_RE.match(ch):
                units.append((ch, st))
                i += 1
            elif ch.isspace():
                j = i
                while j < n and text[j].isspace():
                    j += 1
                units.append((text[i:j], st))
                i = j
            else:
                j = i
                while j < n and not text[j].isspace() and not CJK_RE.match(text[j]):
                    j += 1
                units.append((text[i:j], st))
                i = j
    lines, cur, curw = [], [], 0.0
    for u, st in units:
        w = fonts[st["f"]].width(u, st["sz"]) + st.get("sp", 0) * len(u)
        if u.isspace():
            if not cur:
                continue
            if curw + w > maxw:
                lines.append(cur)
                cur, curw = [], 0.0
                continue
            cur.append((u, st))
            curw += w
            continue
        if cur and curw + w > maxw:
            # hanging punctuation: allow the closing mark to stay on the line
            if u and u[0] in CLOSE and curw + w <= maxw + st["sz"] * 0.55:
                cur.append((u, st))
                curw += w
                continue
            lines.append(cur)
            cur, curw = [], 0.0
        cur.append((u, st))
        curw += w
    if cur:
        lines.append(cur)
    return lines or [[("", runs[0][1] if runs else {"f": "B", "sz": 9.2, "col": C["ink"]})]]


# ---------------------------------------------------------------- code highlight
KW = set("""def class return if elif else for while in not and or is None True False import from as with
lambda yield try except finally raise break continue pass global nonlocal assert del await async""".split())
BI = set("""len range print int str list dict set tuple sum max min abs sorted enumerate zip map filter
any all isinstance type ord chr bool float reversed divmod bytes deque heapq ListNode TreeNode defaultdict
Counter sys math""".split())
TOK = re.compile(r"(?P<cmt>#[^\n]*)|(?P<str>\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')"
                 r"|(?P<num>\b\d+(?:\.\d+)?\b)|(?P<w>[A-Za-z_][A-Za-z_0-9]*)")


def code_runs(src):
    out = []
    for line in (src or "").rstrip("\n").split("\n"):
        runs, pos = [], 0
        for m in TOK.finditer(line):
            if m.start() > pos:
                runs.append((line[pos:m.start()], C["ink"]))
            pos = m.end()
            if m.group("cmt"):
                runs.append((m.group("cmt"), C["cmt"]))
            elif m.group("str"):
                runs.append((m.group("str"), C["str"]))
            elif m.group("num"):
                runs.append((m.group("num"), C["num"]))
            else:
                w = m.group("w")
                runs.append((w, C["kw"] if w in KW else (C["bi"] if w in BI else C["ink"])))
        if pos < len(line):
            runs.append((line[pos:], C["ink"]))
        out.append(runs)
    return out


# ---------------------------------------------------------------- document
class Doc:
    def __init__(self, pdf, fonts):
        self.pdf = pdf
        self.f = fonts
        self.pages = []          # list of dict(ops=[], chapter='')
        self.page = None
        self.y = 0
        self.anchors = {}
        self.chapter = ""
        self.col = 0
        self.toc_mode = False
        self.new_page(blank=True)

    # ---------- primitives
    def _segments(self, text, fk):
        segs = []
        cur = None
        buf = []
        for ch in text:
            f = fk
            if self.f[fk].gid(ch) == 0:
                alt = "B" if fk != "B" else "M"
                if self.f[alt].gid(ch) != 0:
                    f = alt
                else:
                    f = None
            if f is None:
                if buf:
                    segs.append((cur, "".join(buf)))
                    buf = []
                cur = None
                continue
            if f != cur:
                if buf:
                    segs.append((cur, "".join(buf)))
                buf = [ch]
                cur = f
            else:
                buf.append(ch)
        if buf:
            segs.append((cur, "".join(buf)))
        return segs

    def T(self, x, ytop, text, fk, sz, color, bold=False, sp=0):
        if not text:
            return
        r, g, b = color
        py = PH - ytop
        for f, seg in self._segments(text, fk):
            fo = self.f[f]
            hexs = fo.encode(seg)
            if not hexs:
                continue
            self.page["ops"].append(
                b"BT /%s %.2f Tf %.3f %.3f %.3f rg %.3f Tc 1 0 0 1 %.2f %.2f Tm <%s> Tj ET"
                % (fo.name.encode(), sz, r, g, b, sp, x, py, hexs.encode()))
            if bold:
                self.page["ops"].append(
                    b"BT /%s %.2f Tf %.3f %.3f %.3f rg %.3f Tc 1 0 0 1 %.2f %.2f Tm <%s> Tj ET"
                    % (fo.name.encode(), sz, r, g, b, sp, x + 0.34, py, hexs.encode()))
            x += fo.width(seg, sz) + sp * len(seg)

    def tw(self, text, fk, sz, sp=0):
        """measured width of text with font fallback"""
        w = 0
        for f, seg in self._segments(text, fk):
            w += self.f[f].width(seg, sz) + sp * len(seg)
        return w

    def rect(self, x, ytop, w, h, color, stroke=None, lw=0.6):
        r, g, b = color
        py = PH - ytop - h
        if stroke:
            sr, sg, sb = stroke
            self.page["ops"].append(b"%.3f %.3f %.3f rg %.3f %.3f %.3f RG %.2f w %.2f %.2f %.2f %.2f re B"
                                    % (r, g, b, sr, sg, sb, lw, x, py, w, h))
        else:
            self.page["ops"].append(b"%.3f %.3f %.3f rg %.2f %.2f %.2f %.2f re f" % (r, g, b, x, py, w, h))

    def hline(self, x0, x1, ytop, color, lw=0.6, dash=None):
        r, g, b = color
        d = b"[2 2] 0 d " if dash else b"[] 0 d "
        self.page["ops"].append(b"%.3f %.3f %.3f RG %.2f w %s%.2f %.2f m %.2f %.2f l S"
                                % (r, g, b, lw, d, x0, PH - ytop, x1, PH - ytop))

    def grad(self, x, ytop, w, h, sh, c0=None):
        py = PH - ytop - h
        self.page["ops"].append(b"q %.2f %.2f %.2f %.2f re W n /Sh%d sh Q" % (x, py, w, h, sh))

    # ---------- pages
    def new_page(self, blank=False, fixed=False):
        self.pdf.add_page()
        self.pages.append({"ops": [], "chapter": self.chapter, "num": len(self.pages),
                           "fixed": fixed})
        self.page = self.pages[-1]
        self.y = MT

    def ensure(self, h, keep=0):
        if self.y + h + keep > PH - MB:
            self.new_page()

    # ---------- measuring
    def text_w(self, runs, fonts=None):
        fonts = fonts or self.f
        return sum(fonts[st["f"]].width(t, st["sz"]) + st.get("sp", 0) * len(t) for t, st in runs)

    # ---------- blocks
    def para(self, runs, sz=9.2, leading=15.0, maxw=None, x=None, color=None, indent=0,
             bold=False, keep=0, before=0, after=0):
        maxw = maxw or CW
        if isinstance(runs, str):
            runs = [(runs, {"f": "B", "sz": sz, "col": color or C["ink"], "bold": bold})]
        for t, st in runs:
            st.setdefault("sz", sz)
            st.setdefault("f", "B")
            st.setdefault("col", color or C["ink"])
        lines = wrap_runs(runs, maxw - indent, self.f)
        if before:
            self.ensure(before + leading * min(len(lines), 2))
            self.y += before
        for ln in lines:
            self.ensure(leading, keep)
            x0 = (x if x is not None else ML) + indent
            for t, st in ln:
                self.T(x0, self.y + st.get("sz", sz) * 0.92, t, st["f"], st.get("sz", sz),
                       st.get("col", C["ink"]), st.get("bold", False), st.get("sp", 0))
                x0 += self.tw(t, st["f"], st.get("sz", sz)) + st.get("sp", 0) * len(t)
            self.y += leading
        self.y += after

    def code(self, src, sz=7.75, leading=11.0, pad=6.0, indent=0, bar=True):
        runs_lines = code_runs(src)
        maxw = CW - indent - 2 * pad - (2.5 if bar else 0)
        # wrap long lines by characters
        disp = []
        for runs in runs_lines:
            line, w = [], 0.0
            for t, col in runs:
                buf = ""
                for ch in t:
                    cw = self.tw(ch, "M", sz)
                    if w + cw > maxw and (line or buf):
                        if buf:
                            line.append((buf, col)); buf = ""
                        disp.append(line)
                        line, w = [], 0.0
                    buf += ch
                    w += cw
                if buf:
                    line.append((buf, col))
            disp.append(line)
        i = 0
        first = True
        if len(disp) <= 22:
            need_h = len(disp) * leading + 2 * pad
            if self.y + need_h > PH - MB and self.y > MT + 30:
                self.new_page()
        while i < len(disp):
            avail_top = self.y + (2 if first else 0)
            room = (PH - MB) - avail_top - 2 * pad
            nfit = max(1, int(room // leading))
            if nfit < 6 and (PH - MB) - self.y > 40:
                self.new_page()
                room = (PH - MB) - self.y - 2 * pad
                nfit = max(1, int(room // leading))
            chunk = disp[i:i + nfit]
            h = len(chunk) * leading + 2 * pad
            self.ensure(h + (2 if first else 0))
            if self.y + h > PH - MB and len(chunk) < len(disp):
                nfit = max(1, int(((PH - MB) - self.y - 2 * pad) // leading))
                chunk = disp[i:i + nfit]
                h = len(chunk) * leading + 2 * pad
            pad_t = 2 if first else 0
            self.y += pad_t
            self.rect(ML + indent, self.y, CW - indent, h, C["codebg"],
                      stroke=(0.887, 0.908, 0.937))
            if bar:
                self.rect(ML + indent, self.y, 2.4, h, C["blue"])
            yy = self.y + pad + sz * 0.95
            for ln in chunk:
                xx = ML + indent + pad + (2.5 if bar else 0)
                for t, col in ln:
                    self.T(xx, yy, t, "M", sz, col)
                    xx += self.tw(t, "M", sz)
                yy += leading
            self.y += h
            i += len(chunk)
            first = False
            if i < len(disp):
                self.new_page()

    def bullets(self, items, sz=9.0, leading=14.6, marker="•", mcol="blue", indent=13, gap=2):
        for k, runs in enumerate(items):
            if isinstance(runs, str):
                runs = [(runs, {})]
            runs = [("", {"f": "B", "sz": sz, "col": C["ink"]})] + [
                (t, {**st, "sz": sz}) for t, st in runs]
            for t, st in runs:
                st.setdefault("f", "B"); st.setdefault("col", C["ink"]); st.setdefault("sz", sz)
            lines = wrap_runs(runs, CW - indent, self.f)
            if self.y + leading * len(lines) + gap > PH - MB:
                self.new_page()
            x0 = ML
            mk = marker if marker != "num" else f"{k + 1}."
            if marker == "num":
                self.T(ML + 1, self.y + sz * 0.92, mk, "B", sz, C[mcol], bold=True)
            else:
                self.T(ML + 2, self.y + sz * 0.92, mk, "B", sz, C[mcol])
            for ln in lines:
                xx = ML + indent
                for t, st in ln:
                    self.T(xx, self.y + st["sz"] * 0.92, t, st["f"], st["sz"], st["col"], st.get("bold"))
                    xx += self.tw(t, st["f"], st["sz"])
                self.y += leading
            self.y += gap

    # ---------- composite blocks
    def card_head(self, idx, title, diff, tags, anchor=None):
        self.ensure(64, keep=70)
        if anchor:
            self.anchors[anchor] = self.page["num"] - 1
        self.y += 4
        self.hline(ML, ML + CW, self.y, C["blue2"], 1.3)
        self.y += 13
        self.T(ML, self.y, idx, "B", 7.4, C["gray2"])
        x = ML + 34
        ts = 12.6
        while self.tw(title, "B", ts) > CW - 34 - 92 and ts > 9.5:
            ts -= 0.4
        self.T(x, self.y, title, "B", ts, C["navy"], bold=True)
        # badge
        bw = self.tw(diff, "B", 6.6) + 9
        bx = ML + CW - bw
        col = C[DIFF_COL.get(diff, "mid")]
        self.rect(bx, self.y - 7.4, bw, 10.4, col)
        self.T(bx + 4.5, self.y - 0.2, diff, "B", 6.6, C["white"])
        # tags right of title
        if tags:
            tw = self.tw(tags, "B", 6.6) + 8
            tx = bx - 6 - tw
            if tx > x + self.tw(title, "B", ts) + 10:
                self.rect(tx, self.y - 7.4, tw, 10.4, (0.93, 0.95, 0.97))
                self.T(tx + 4, self.y - 0.2, tags, "B", 6.6, C["gray"])
        self.y += 9
        self.hline(ML, ML + CW, self.y, (0.86, 0.89, 0.93), 0.6)

    def keybox(self, text):
        sz, leading = 9.2, 13.6
        runs = [(text, {"f": "B", "sz": sz, "col": C["keyink"]})]
        lines = wrap_runs(runs, CW - 54, self.f)
        h = len(lines) * leading + 9
        self.ensure(h + 4)
        self.y += 3
        self.rect(ML, self.y, CW, h, C["keybg"], stroke=C["keybr"], lw=0.7)
        lw_ = self.tw("记忆", "B", 6.8) + 9
        self.rect(ML + 6, self.y + (h - 11) / 2, lw_, 11, C["accent"])
        self.T(ML + 6 + 4.5, self.y + (h - 11) / 2 + 8, "记忆", "B", 6.8, C["white"])
        yy = self.y + 4 + sz * 0.92
        for ln in lines:
            xx = ML + 6 + lw_ + 7
            for t, st in ln:
                self.T(xx, yy, t, "B", sz, st["col"])
                xx += self.tw(t, "B", sz)
            yy += leading
        self.y += h

    def trapbox(self, text):
        sz, leading = 8.6, 13.0
        runs = [("易错　", {"f": "B", "sz": sz, "col": C["trapink"], "bold": True}),
                (text, {"f": "B", "sz": sz, "col": C["trapink"]})]
        lines = wrap_runs(runs, CW - 16, self.f)
        h = len(lines) * leading + 7
        self.ensure(h + 4)
        self.y += 2
        self.rect(ML, self.y, CW, h, C["trapbg"])
        self.rect(ML, self.y, 2.2, h, C["trapbr"])
        yy = self.y + 3.5 + sz * 0.92
        for ln in lines:
            xx = ML + 8
            for t, st in ln:
                self.T(xx, yy, t, "B", sz, C["trapink"], bold=st.get("bold", False))
                xx += self.tw(t, "B", sz)
            yy += leading
        self.y += h

    def section_banner(self, kicker, title, meta, anchor=None, chapter=None):
        self.ensure(120)
        if anchor:
            self.anchors[anchor] = self.page["num"] - 1
        if chapter:
            self.chapter = chapter
            self.page["chapter"] = chapter
        h = 86
        sh = self.pdf.add_shading(ML, PH - self.y - h, ML + CW, PH - self.y, (0.05, 0.14, 0.31), (0.11, 0.27, 0.55))
        self.grad(ML, self.y, CW, h, sh)
        self.T(ML + 18, self.y + 26, kicker, "B", 8.6, C["accent"], sp=1.6)
        self.T(ML + 18, self.y + 58, title, "B", 24, C["white"], bold=True, sp=0.8)
        self.T(ML + 18, self.y + 76, meta, "B", 8.4, (0.78, 0.85, 0.95))
        self.y += h

    def label(self, text, color="blue", before=6.0, keep=54.0):
        self.ensure(16 + keep)
        self.y += before
        col = color if isinstance(color, tuple) else C[color]
        self.T(ML, self.y, text, "B", 7.6, col, bold=True)
        self.y += 3.5

    def table(self, header, rows, widths, anchor=None, sz=8.0, leading=11.4, pad=3.0,
              head_bg=(0.93, 0.95, 0.98), zebra=True):
        if anchor:
            self.anchors[anchor] = self.page["num"] - 1
        tw = sum(widths)
        scale = CW / tw if abs(tw - CW) > 0.5 else 1.0
        widths = [w * scale for w in widths]

        def prep(cells):
            out = []
            for i, cell in enumerate(cells):
                if isinstance(cell, str):
                    cell = [(cell, {"f": "B", "sz": sz})]
                out.append(wrap_runs(cell, widths[i] - 2 * pad, self.f))
            return out

        def draw_row(wrapped, is_head=False, zebra_on=True):
            h = max(len(l) for l in wrapped) * leading + 2 * pad - 2
            if self.y + h > PH - MB:
                self.new_page()
                if header and not is_head:
                    draw_row(prep(header), True, False)
            r, g, b = head_bg if is_head else ((0.984, 0.988, 0.996) if zebra_on else C["white"])
            self.rect(ML, self.y, sum(widths), h, (r, g, b))
            x = ML
            for i, lines in enumerate(wrapped):
                yy = self.y + pad + sz * 0.9
                for ln in lines:
                    xx = x + pad
                    for t, s2 in ln:
                        self.T(xx, yy, t, "B", sz, C["navy"] if is_head else C["ink"], bold=is_head)
                        xx += self.tw(t, "B", sz)
                    yy += leading
                x += widths[i]
            self.hline(ML, ML + sum(widths), self.y + h, C["rule"], 0.5)
            x = ML
            for wd in widths:
                self.hline(x, x, self.y, C["rule"], 0.4)
                x += wd
            self.y += h

        if header:
            draw_row(prep(header), True, True)
        for i, row in enumerate(rows):
            draw_row(prep(row), False, zebra and i % 2 == 1)
        self.y += 6

    def footer(self):
        for p in self.pages[1:]:
            n = p["num"]
            ops = []
            ops.append(b"0.84 0.87 0.91 RG 0.5 w %.2f %.2f m %.2f %.2f l S"
                       % (ML, 24, ML + CW, 24))
            p["ops"] = ops + p["ops"]

# ---------------------------------------------------------------- builder
def load_all():
    idx = json.load(io.open(os.path.join(W, "index.json"), encoding="utf-8"))
    contents = {}
    for f in sorted(os.listdir(OUT)):
        if f.startswith("g") and f.endswith(".json"):
            try:
                data = json.load(io.open(os.path.join(OUT, f), encoding="utf-8"))
            except Exception as e:
                print("!!", f, e)
                continue
            for d in data:
                contents[str(d["id"])] = d
    hot = OrderedDict()
    for it in idx["hot"]:
        hot.setdefault(it["cat"], []).append(it)
    ext = OrderedDict()
    for it in idx["extras"]:
        ext.setdefault(it["cat"], []).append(it)
    return idx, contents, hot, ext
