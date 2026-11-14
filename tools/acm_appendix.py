# -*- coding: utf-8 -*-
"""附录 C：ACM 模式输入输出模板。所有示例程序都带样例输入，可本地跑通校验。"""

SECTIONS = []


def add(sid, title, intro, code, sample, note):
    SECTIONS.append(dict(id=sid, title=title, intro=intro, code=code.strip("\n"),
                         sample=sample.strip("\n"), note=note))


add("C.1", "万能开头：一次把所有输入读成 token",
    "九成的 ACM 题都可以这样读：把全部输入一次性切分成 token 列表，再用一个游标依次往后取。换行、"
    "多余空格、行末回车都不受影响，也不必关心「这一行到底几个数」。四门语言一一对应：Python 是 "
    "sys.stdin.read().split()，C++ 是 cin >>，Java 是 StreamTokenizer，Go 是 os.ReadFile 加 strings.Fields。",
    r'''
import sys

def main():
    data = sys.stdin.read().split()
    if not data:               # 空输入直接返回，避免评测机传空文件时报错
        return
    p = 0
    n = int(data[p]); p += 1
    nums = list(map(int, data[p:p + n])); p += n

    print(sum(nums), max(nums))

if __name__ == "__main__":
    main()
''',
    "输入：\n5\n3 1 4 1 5\n输出：\n14 5",
    "token 都是字符串，取数时记得转成整数；游标要自己维护，不要用下标去猜行号。")

add("C.2", "按行读：需要保留行内空格时",
    "如果题目是「先给行数 n，接下来 n 行、每行一句话」，就要一行一行读、再自己切分；"
    "一次读全部 token 的写法会把换行信息丢掉，就没法知道哪几个词属于同一行。",
    r'''
import sys

def main():
    n = int(sys.stdin.readline())
    out = []
    for _ in range(n):
        line = sys.stdin.readline().rstrip("\n")   # 只去掉行尾换行，保留行内空格
        out.append(str(len(line.split())))
    print("\n".join(out))

if __name__ == "__main__":
    main()
''',
    "输入：\n2\nhello world\na b c\n输出：\n2\n3",
    "去行尾空白时注意别把行内空格一起去掉；只想砍掉换行，就只去换行符。")

add("C.3", "多组数据：第一行给组数 T",
    "在线笔试最常见的形式：第一行 T，之后每组「先一个 n，再 n 个数」。"
    "注意每组都要重新初始化变量，答案先攒到容器里、最后一次输出，避免逐行输出带来的开销。",
    r'''
import sys

def main():
    data = sys.stdin.read().split()
    p = 0
    t = int(data[p]); p += 1
    out = []
    for _ in range(t):
        n = int(data[p]); p += 1
        nums = list(map(int, data[p:p + n])); p += n
        out.append(str(sum(nums)))
    print("\n".join(out))

if __name__ == "__main__":
    main()
''',
    "输入：\n3\n3\n1 2 3\n2\n10 20\n1\n5\n输出：\n6\n30\n5",
    "T 组之间不要残留上一组的状态；输出逐行，不要多打空行。")

add("C.4", "多组数据：不给组数，读到文件末尾",
    "有些题不给组数，一直读到文件末尾（每行两个数求 a+b 那种）。逐行读，读到空行或读不到就停；"
    "下面这种最稳，还能顺手跳过空行。",
    r'''
import sys

def main():
    out = []
    for line in sys.stdin:
        line = line.strip()
        if not line:           # 跳过空行
            continue
        a, b = map(int, line.split())
        out.append(str(a + b))
    print("\n".join(out))

if __name__ == "__main__":
    main()
''',
    "输入：\n1 2\n3 4\n5 6\n输出：\n3\n7\n11",
    "读到末尾时别用会抛异常的整行函数，要自己判断是否已读完。")

add("C.5", "矩阵：先给 m n，再给 m 行每行 n 个",
    "二维数组一般是「第一行 m n，后面 m 行、每行 n 个数」。按行切片最省事：一次取一行（n 个数），"
    "游标往后推 n。不要去数空格，也不要假设每行只有 n 个 token。",
    r'''
import sys

def main():
    data = sys.stdin.read().split()
    p = 0
    m, n = int(data[p]), int(data[p + 1]); p += 2
    grid = []
    for _ in range(m):
        grid.append(list(map(int, data[p:p + n])))
        p += n

    for row in grid:
        print(sum(row))

if __name__ == "__main__":
    main()
''',
    "输入：\n2 3\n1 2 3\n4 5 6\n输出：\n6\n15",
    "先读 m 再读 n，顺序别记反；一行的元素要一次性读完再进下一行。")

add("C.6", "网格：m 行字符串（岛屿、迷宫这类题）",
    "网格题的输入通常是「m n，然后 m 行、每行一个长度 n 的字符串」，比如 0/1 地图。"
    "整行读进来后拆成字符数组，注意字符是 \"1\" 而不是数字 1。",
    r'''
import sys
from collections import deque

def main():
    data = sys.stdin.read().split()
    m, n = int(data[0]), int(data[1])
    grid = [list(s) for s in data[2:2 + m]]      # 每行一个字符串

    seen = [[False] * n for _ in range(m)]
    blocks = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] != "1" or seen[i][j]:
                continue
            blocks += 1
            q = deque([(i, j)])
            seen[i][j] = True
            while q:
                x, y = q.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == "1" and not seen[nx][ny]:
                        seen[nx][ny] = True
                        q.append((nx, ny))
    print(blocks)

if __name__ == "__main__":
    main()
''',
    "输入：\n3 4\n1100\n1100\n0011\n输出：\n2",
    "比较时用字符 \"1\"；网格坐标先判越界再访问，顺序反了会下标越界。")

add("C.7", "整行字符串：一行里有空格",
    "「反转字符串里的单词」「统计词数」这类题必须整行读；一次读全部 token 会把整行拆散。"
    "读进来后自己切词、再拼回去，行内的连续空格会被自动压成一个。",
    r'''
import sys

def main():
    line = sys.stdin.readline().strip()
    words = line.split()
    print(" ".join(words[::-1]))

if __name__ == "__main__":
    main()
''',
    "输入：\nthe sky is blue\n输出：\nblue is sky the",
    "别只取第一个 token；整行场景一定要按行读。")

add("C.8", "n 个数 + q 次查询（前缀和）",
    "「先给数组，再给 q 组 l r 询问区间和」是笔试里最常见的组合。"
    "读完数组后用游标继续读 q 组数，前缀和 pre[i] 表示前 i 个元素之和。",
    r'''
import sys

def main():
    data = sys.stdin.read().split()
    p = 0
    n, q = int(data[p]), int(data[p + 1]); p += 2
    a = list(map(int, data[p:p + n])); p += n

    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + a[i]

    out = []
    for _ in range(q):
        l, r = int(data[p]), int(data[p + 1]); p += 2
        out.append(str(pre[r] - pre[l - 1]))
    print("\n".join(out))

if __name__ == "__main__":
    main()
''',
    "输入：\n5 2\n1 2 3 4 5\n1 3\n2 5\n输出：\n6\n14",
    "前缀和下标从 1 开始更省心，pre[0]=0；查询区间是闭区间 [l, r]。")

add("C.9", "链表：自己定义 ListNode、自己建表、自己输出",
    "LeetCode 里 head 是现成的，ACM 里要自己建。标准三件套：ListNode 定义、用哨兵节点尾插建表、"
    "遍历输出成一行。下面这题顺便把链表反转也做了。",
    r'''
import sys

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build(vals):
    dummy = ListNode()
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    vals = list(map(int, data[1:1 + n]))
    head = build(vals)

    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt

    out = []
    while prev:
        out.append(str(prev.val))
        prev = prev.next
    print(" ".join(out))

if __name__ == "__main__":
    main()
''',
    "输入：\n5\n1 2 3 4 5\n输出：\n5 4 3 2 1",
    "链表题一律用哨兵节点；输出时先攒进容器再一次性输出，别边遍历边打印。")

add("C.10", "二叉树：层序数组建树（null 表示空）",
    "树的输入几乎都是「节点数 n，然后层序数组，null 表示空节点」——正好是 LeetCode 序列化的逆过程。"
    "用队列逐个补左右孩子，遇到 null 就跳过，千万别把 null 也建成节点。",
    r'''
import sys
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build(tokens):
    if not tokens or tokens[0] == "null":
        return None
    root = TreeNode(int(tokens[0]))
    q = deque([root])
    i = 1
    while q and i < len(tokens):
        node = q.popleft()
        if tokens[i] != "null":
            node.left = TreeNode(int(tokens[i]))
            q.append(node.left)
        i += 1
        if i < len(tokens) and tokens[i] != "null":
            node.right = TreeNode(int(tokens[i]))
            q.append(node.right)
        i += 1
    return root

def main():
    sys.setrecursionlimit(10 ** 6)
    data = sys.stdin.read().split()
    root = build(data[1:])          # 第一个是 n，后面是层序值

    out = []
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        out.append(str(node.val))
        dfs(node.right)
    dfs(root)
    print(" ".join(out))

if __name__ == "__main__":
    main()
''',
    "输入：\n7\n1 2 3 4 5 6 7\n输出：\n4 2 5 1 6 3 7",
    "递归深度可能到 1e5，记得调大递归深度上限；输出层序时把空节点统一打成 null。")

add("C.11", "图：n m + m 条边（邻接表 + BFS）",
    "图题最标准的输入是「n m，然后 m 行 u v」，表示一条边。"
    "无向图两个方向都加，有向图只加一次；1 到 n 编号时开 n+1 个桶更省心。",
    r'''
import sys
from collections import deque

def main():
    data = sys.stdin.read().split()
    p = 0
    n, m = int(data[p]), int(data[p + 1]); p += 2
    g = [[] for _ in range(n + 1)]
    for _ in range(m):
        u, v = int(data[p]), int(data[p + 1]); p += 2
        g[u].append(v)
        g[v].append(u)          # 有向图删掉这一行

    s, t = int(data[p]), int(data[p + 1])
    dist = [-1] * (n + 1)
    dist[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v in g[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    print(dist[t])              # 不可达输出 -1

if __name__ == "__main__":
    main()
''',
    "输入：\n4 3\n1 2\n2 3\n3 4\n1 4\n输出：\n3",
    "无向图别漏反向边；dist 初始成 -1 顺便当访问标记，省一个 visited 数组。")

add("C.12", "带权图：u v w（Dijkstra）",
    "带权最短路每条边三个数：u v w。堆里存 (距离, 节点)，出堆时用 d > dist[u] 跳过过期状态。"
    "权重非负才能用 Dijkstra；有负权改用 Bellman-Ford。",
    r'''
import sys
import heapq

def main():
    data = sys.stdin.read().split()
    p = 0
    n, m = int(data[p]), int(data[p + 1]); p += 2
    g = [[] for _ in range(n + 1)]
    for _ in range(m):
        u, v, w = int(data[p]), int(data[p + 1]), int(data[p + 2]); p += 3
        g[u].append((v, w))
        g[v].append((u, w))

    s = int(data[p])
    INF = float("inf")
    dist = [INF] * (n + 1)
    dist[s] = 0
    h = [(0, s)]
    while h:
        d, u = heapq.heappop(h)
        if d > dist[u]:
            continue
        for v, w in g[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(h, (dist[v], v))

    print(" ".join(str(dist[i]) for i in range(1, n + 1)))

if __name__ == "__main__":
    main()
''',
    "输入：\n4 4\n1 2 1\n2 3 2\n3 4 3\n1 4 10\n1\n输出：\n0 1 3 6",
    "堆里放的是 (距离, 节点)，不是 (节点, 距离)；节点编号从 1 开始时数组要开 n+1。")

add("C.13", "并查集：边表建图",
    "并查集只关心「连不连通」，不需要存邻接表，边读边合并即可。"
    "路径压缩写成循环，避免递归过深；最后输出连通块个数 = n - 合并成功次数。",
    r'''
import sys

def main():
    data = sys.stdin.read().split()
    p = 0
    n, m = int(data[p]), int(data[p + 1]); p += 2
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    merged = 0
    for _ in range(m):
        u, v = int(data[p]), int(data[p + 1]); p += 2
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            merged += 1

    print(n - merged)          # 连通块个数

if __name__ == "__main__":
    main()
''',
    "输入：\n5 3\n1 2\n2 3\n4 5\n输出：\n2",
    "并查集只合并不回退，不能用来删边；输出的是连通块数，不是边数。")

add("C.14", "拓扑排序：有向图 + 入度",
    "拓扑排序用入度数组 + 队列：先把入度为 0 的点入队，出队时把邻居入度减一，减到 0 再入队。"
    "如果最后出队数量不等于 n，说明有环。",
    r'''
import sys
from collections import deque

def main():
    data = sys.stdin.read().split()
    p = 0
    n, m = int(data[p]), int(data[p + 1]); p += 2
    g = [[] for _ in range(n + 1)]
    indeg = [0] * (n + 1)
    for _ in range(m):
        u, v = int(data[p]), int(data[p + 1]); p += 2
        g[u].append(v)
        indeg[v] += 1

    q = deque(i for i in range(1, n + 1) if indeg[i] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(str(u))
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    print(" ".join(order) if len(order) == n else "-1")

if __name__ == "__main__":
    main()
''',
    "输入：\n4 3\n1 2\n1 3\n3 4\n输出：\n1 2 3 4",
    "有向图只加一次边；输出数量不足 n 就是有环，按题目要求输出 -1 或空。")

add("C.15", "输出格式：一行、每行一个、小数、二维结果",
    "输出格式错等于答案错，这是 ACM 模式最常见的冤枉分。下面一段程序演示四种最常用写法："
    "一行空格分隔、每行一个、保留两位小数、二维结果先给行数再逐行。",
    r'''
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    print(" ".join(map(str, nums)))      # 一行，空格分隔
    for x in nums:                       # 每行一个
        print(x)
    print(f"{sum(nums) / n:.2f}")        # 保留两位小数
    rows = [[1, 2], [3]]                 # 二维：先行数，再每行
    print(len(rows))
    for r in rows:
        print(*r)

if __name__ == "__main__":
    main()
''',
    "输入：\n4\n1 2 3 4\n输出：\n1 2 3 4\n1\n2\n3\n4\n2.50\n2\n1 2\n3",
    "想一行输出多个值就用空格拼接；不要残留调试输出。")


if __name__ == "__main__":
    import subprocess, sys
    sys.stdout.reconfigure(encoding="utf-8")
    ok = 0
    for s in SECTIONS:
        sample = s["sample"]
        # sample = "输入：\n...\n输出：\n..."
        body = sample.split("输入：", 1)[1]
        if "输出：" in body:
            inp, out = body.split("输出：", 1)
        else:
            inp, out = body, ""
        r = subprocess.run([sys.executable, "-c", s["code"]], input=inp.strip("\n") + "\n",
                           capture_output=True, text=True, encoding="utf-8", timeout=20)
        got = r.stdout.strip("\n")
        expect = out.strip().strip("\n")
        status = "OK" if r.returncode == 0 else "CRASH"
        if expect and got != expect.replace(" / ", "\n"):
            status = "MISMATCH"
        if status == "OK":
            ok += 1
        print(f"{s['id']} {s['title'][:18]:20s} {status}")
        if status != "OK":
            print("  got:", got.replace("\n", " | ")[:200])
            print("  exp:", expect.replace("\n", " | ")[:200])
            print("  err:", (r.stderr or "").strip().splitlines()[-1:])
    print(f"\n{ok}/{len(SECTIONS)} passed")
