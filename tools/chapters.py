# -*- coding: utf-8 -*-
"""每类题型的「ACM 模式输入输出」导语 + 模板代码（作者自写，供 PDF 章节开头使用）。"""

CH = {}
_PART = [1]


def setpart(n):
    _PART[0] = n


def add(key, lead, code, out):
    CH[f"{_PART[0]}|{key}"] = {"lead": lead, "code": code.strip("\n"), "out": out}


# ---------------- Part I ----------------
setpart(1)
add("哈希", "哈希/集合类题目的输入几乎都是「一个 n，然后 n 个数（或 n 个字符串），最后一行目标值」。"
     "ACM 模式里不要用 input() 逐行读，统一 `sys.stdin.read().split()` 一次读成 token 列表，用游标往后取，"
     "这样换行、空格、多组数据的差异都被抹平了。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    p = 0
    n = int(data[p]); p += 1
    nums = [int(x) for x in data[p:p + n]]; p += n
    target = int(data[p]); p += 1

    # 把解法里的 Solution 类粘在这里
    print(Solution().twoSum(nums, target))

if __name__ == "__main__":
    main()
""",
    "只打印最终答案，不要打印「please input」这类提示；列表输出用 `print(*ans)` 或 `print(ans)`，"
    "题目要求哪种格式就照哪种来。")

add("双指针", "双指针题通常给「n + n 个数」，有的题（如三数之和）还要输出二维结果。"
     "把数组整体读进来即可，双指针本身在数组上跑，不需要额外输入。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    ans = Solution().threeSum(nums)
    print(len(ans))
    for row in ans:
        print(*row)

if __name__ == "__main__":
    main()
""",
    "二维答案统一「先输出行数，再每行输出一行」，机器判题一般都能过；如果题目只要求输出数量，就只打印 len。")

add("滑动窗口", "滑动窗口题只需要「n + 数组」或者「一个字符串 + 一个模式串」。"
     "字符串直接当 token 读，不要用 input() 再去处理引号和空格。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    s = data[0]
    p = data[1] if len(data) > 1 else ""

    print(Solution().lengthOfLongestSubstring(s))

if __name__ == "__main__":
    main()
""",
    "字符串题不用把它拆成字符数组，Python 里 str 本身可下标/切片，直接用。")

add("子串", "子串/区间类题目的输入是「数组 + 目标值 k」或「字符串 + 模式串」，"
     "读入后直接调用方法即可；注意 k 可能是负数或大于数组和，别提前 return 错。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    nums = list(map(int, data[2:2 + n]))

    print(Solution().subarraySum(nums, k))

if __name__ == "__main__":
    main()
""",
    "输出单个数字时直接 print(int)；输出下标列表时按题目要求决定是否需要先输出长度。")

add("普通数组", "数组类是 ACM 模式最基础的形态：第一行 n，第二行 n 个数。"
     "偶尔会先给 m、n 两个维度，或者给多组数据（读到 EOF 为止），模板里给了通用写法。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    p = 0
    out = []
    while p < len(data):                      # 多组数据：读到 EOF
        n = int(data[p]); p += 1
        nums = list(map(int, data[p:p + n])); p += n
        out.append(str(Solution().maxSubArray(nums)))
    print("\\n".join(out))

if __name__ == "__main__":
    main()
""",
    "如果题目只有一组数据，把 while 换成一次读取更直观；多组数据时千万别在循环里 print 提示语。")

add("矩阵", "矩阵题先给 m、n，再给 m 行、每行 n 个数（或直接给 m*n 个 token）。"
     "用「按行切片」的方式构造二维列表，比逐行 input() 稳。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    m, n = int(data[0]), int(data[1])
    flat = list(map(int, data[2:2 + m * n]))
    grid = [flat[i * n:(i + 1) * n] for i in range(m)]

    ans = Solution().spiralOrder(grid)
    print(*ans)

if __name__ == "__main__":
    main()
""",
    "输出矩阵时逐行 print(*row)；原地修改类题（如矩阵置零、旋转图像）直接在 grid 上改，最后再把 grid 打出来。")

add("链表", "链表题在 ACM 模式里要自己建表：先读节点值数组，再按需读 pos（环的位置）等附加参数。"
     "面试/机试里最省事的写法是「哨兵 + 尾插」，建完再调用解法，最后把结果链表拼成列表打印。",
    """
import sys

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build(vals):
    dummy = ListNode(0)
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

def dump(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    vals = list(map(int, data[1:1 + n]))
    head = build(vals)

    res = Solution().reverseList(head)
    print(*dump(res))

if __name__ == "__main__":
    main()
""",
    "环形链表类题目要额外读一个 pos（-1 表示无环），把尾节点接到第 pos 个节点上再判环；"
    "输出链表一律 dump 成空格分隔的一行。")

add("二叉树", "二叉树题在 ACM 模式里是「层序数组」，用 null / None 表示空节点——"
     "本质是 LeetCode 序列化的逆过程。用队列逐个建节点，遇到 null 就跳过，千万别把 null 当子节点建出来。",
    """
import sys
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build(tokens):
    if not tokens or tokens[0] in ("null", "None", "#"):
        return None
    root = TreeNode(int(tokens[0]))
    q = deque([root])
    i = 1
    while q and i < len(tokens):
        node = q.popleft()
        if i < len(tokens) and tokens[i] not in ("null", "None", "#"):
            node.left = TreeNode(int(tokens[i]))
            q.append(node.left)
        i += 1
        if i < len(tokens) and tokens[i] not in ("null", "None", "#"):
            node.right = TreeNode(int(tokens[i]))
            q.append(node.right)
        i += 1
    return root

def main():
    data = sys.stdin.read().split()
    root = build(data[1:])          # 第一行是 n，后面是层序值

    print(Solution().maxDepth(root))

if __name__ == "__main__":
    main()
""",
    "递归解法的深度可能到 1e5，记得 `sys.setrecursionlimit(10**6)`；"
    "输出层序结果时把 None 统一打成 null。")

add("图论", "图论题输入最常见三种：① n 条边，每行 u v；② 邻接矩阵 n×n；③ 网格地图 m 行字符串。"
     "建图统一用 `g = [[] for _ in range(n+1)]`（1-indexed），再 DFS/BFS/并查集/拓扑排序。",
    """
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
        g[v].append(u)               # 无向图才加这一行

    seen = [False] * (n + 1)
    cnt = 0
    for s in range(1, n + 1):
        if seen[s]:
            continue
        cnt += 1
        q = deque([s]); seen[s] = True
        while q:
            u = q.popleft()
            for v in g[u]:
                if not seen[v]:
                    seen[v] = True
                    q.append(v)
    print(cnt)

if __name__ == "__main__":
    main()
""",
    "网格类题目（岛屿数量等）把每行读成字符串再转 list；"
    "拓扑排序记得输出「入度为 0 的节点顺序」，无解输出空或题目要求的值。")

add("回溯", "回溯题输入极简：通常只有一个 n，或者「n + 数组」，或者「字符串 + 字典」。"
     "输出的是所有方案，ACM 模式里要自己决定按什么格式打印（一般「先方案数，再每行一个方案」）。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    ans = Solution().permute(nums)
    print(len(ans))
    for row in ans:
        print(*row)

if __name__ == "__main__":
    main()
""",
    "回溯结果数量可能爆炸（N 皇后 n=9 就有 352 组），打印前先确认数据规模；"
    "剪枝条件写在递归入口，别放在 append 之后。")

add("二分查找", "二分题输入是「n + 有序数组 + target」，或者「矩阵 m n + m*n 个数 + target」。"
     "读入后用左闭右开/左闭右闭其中一种写法，全程不要混用。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))
    target = int(data[1 + n])

    print(Solution().search(nums, target))

if __name__ == "__main__":
    main()
""",
    "返回值是下标就直接 print；返回区间就 print(left, right)；"
    "注意 target 不存在时的返回值约定（-1 还是插入位置）。")

add("栈", "栈/队列题分两类：一类给「数组 + k」，一类要求你实现数据结构（最小栈、LRU）。"
     "实现类的题在 ACM 模式里按操作序列读：第一行操作数 q，之后每行一个操作 + 参数。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    p = 0
    q = int(data[p]); p += 1
    out = []
    for _ in range(q):
        op = data[p]; p += 1
        if op == "push":
            v = int(data[p]); p += 1
            st.push(v)
        elif op == "pop":
            st.pop()
            out.append("null")
        else:                       # top / getMin / get ...
            out.append(str(st.getMin()))
    print("\\n".join(out))

if __name__ == "__main__":
    main()
""",
    "设计类题目输出里的 null 要照打（对应无返回值的操作），不要省略成空行。")

add("堆", "堆题输入是「n + 数组 + k」，或者「操作序列（add / findMedian）」。"
    "Python 只有小根堆：求第 k 大就存负值，求前 k 大就用 size=k 的小根堆。",
    """
import sys
import heapq

def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    nums = list(map(int, data[2:2 + n]))

    h = []
    for v in nums:
        heapq.heappush(h, v)
        if len(h) > k:
            heapq.heappop(h)
    print(h[0])                     # 第 k 大 = 大小为 k 的小根堆堆顶

if __name__ == "__main__":
    main()
""",
    "多组输出时注意每行一个；求中位数那种题要把两个堆（大根堆存负值）的平衡条件写死。")

add("贪心算法", "贪心题输入一般是「n + 数组」，少数是「数组 + 限制值」。"
     "读入后通常要先排序，再一遍扫描；ACM 模式里排序不影响输入格式。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    print(Solution().canJump(nums))

if __name__ == "__main__":
    main()
""",
    "输出布尔值统一 True/False 或题目要求的 1/0；别混着来。")

add("动态规划", "一维 DP 的输入是「n + 数组」或「n + 容量」，二维 DP 常给「两个字符串」或「n + 数组 + 目标」。"
     "状态定义写在注释里，ACM 模式只负责把输入塞进方法。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    print(Solution().rob(nums))

if __name__ == "__main__":
    main()
""",
    "DP 结果可能是 0 或负数，别用 `if ans:` 这种真值判断来决定是否输出。")

add("多维动态规划", "二维 DP 的输入多为「两个字符串 s、t」或「m n + m×n 网格」，"
     "也可能是「物品数 n + 容量」。字符串题直接当 token 读，网格题按行切片构造。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    if len(data) >= 2:
        s, t = data[0], data[1]
        print(Solution().longestCommonSubsequence(s, t))
    else:
        m, n = int(data[0]), int(data[1])
        grid = [[int(x) for x in data[2 + i * n:2 + (i + 1) * n]] for i in range(m)]
        print(Solution().minPathSum(grid))

if __name__ == "__main__":
    main()
""",
    "字符串长度可能到 1000+，DP 表用滚动数组能省内存，但输出格式不受影响。")

add("技巧", "技巧类题目输入差异大：位运算题给「n + 数组」，找重复数给「n+1 个数的数组」，"
     "下一个排列给「n + 数组」。统一按 n 读，能覆盖九成情况。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    print(Solution().singleNumber(nums))

if __name__ == "__main__":
    main()
""",
    "输出数组就 print(*nums)；要求原地修改的题，修改完再打印。")

# ---------------- Part II ----------------
setpart(2)
add("数组", "补充篇的数组题（二分查找、移除元素、螺旋矩阵、长度最小的子数组）在 ACM 模式里"
     "还要注意「原地修改」：机试判题看的是你最后输出的数组，所以改完要打印整个数组。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    k = Solution().removeElement(nums, 2)
    print(k)
    print(*nums[:k])

if __name__ == "__main__":
    main()
""",
    "「返回新长度 k」的题，判题器通常只检查前 k 个元素，打印时记得切片。")

add("链表", "补充篇的链表题（移除链表元素、设计链表、重排链表）都要求自己建表、自己输出。"
     "设计链表类题目按操作序列读：`addAtHead v` / `addAtIndex i v` / `deleteAtIndex i` / `get i`。",
    """
import sys

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build(vals):
    dummy = ListNode(0)
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

def main():
    data = sys.stdin.read().split()
    p = 0
    q = int(data[p]); p += 1
    obj = None
    out = []
    for _ in range(q):
        op = data[p]; p += 1
        if op == "MyLinkedList":
            obj = MyLinkedList(); out.append("null")
        elif op == "addAtHead":
            obj.addAtHead(int(data[p])); p += 1; out.append("null")
        elif op == "get":
            out.append(str(obj.get(int(data[p])))); p += 1
        else:
            obj.deleteAtIndex(int(data[p])); p += 1; out.append("null")
    print("\\n".join(out))

if __name__ == "__main__":
    main()
""",
    "设计类题目的输出是「每个操作的返回值，没有就 null」，一行一个，顺序不能乱。")

add("哈希表", "哈希题输入是「n + 数组」或「字符串 + 字符串」，四数相加这类给四个数组，"
     "读入时按长度切段即可；不要假设每行长度一致。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    print(Solution().fourSumCount(nums, nums, nums, nums))

if __name__ == "__main__":
    main()
""",
    "输出计数直接 print(int)；输出去重后的集合时先排序再打印，保证结果稳定。")

add("字符串", "字符串题注意「读 token 还是读整行」：翻转单词这类题目内部有空格，"
     "必须先 `sys.stdin.readline()` 读整行再 strip，不能 split 后只取第一个 token。",
    """
import sys

def main():
    line = sys.stdin.readline().strip()
    print(Solution().reverseWords(line))

if __name__ == "__main__":
    main()
""",
    "需要保留空格的题用 readline；纯字母/数字串才用 read().split()。")

add("栈与队列", "栈队列题分「表达式求值」（给一整个字符串）和「用栈实现队列」（给操作序列）两类。"
     "表达式里的逆波兰式按 token 读，操作符和数字混在一起时统一当字符串判断。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    print(Solution().evalRPN(data))

if __name__ == "__main__":
    main()
""",
    "结果为整数时注意 Python 的 `/` 是浮点除，要用 `int(a / b)` 或向零截断的写法。")

add("单调栈", "单调栈题给「n + 数组」或「nums1 + nums2」两个数组。栈里存下标，"
     "出栈时才知道答案落在哪一位，所以 ACM 模式只负责把两个数组读进来。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    print(*Solution().nextGreaterElements(nums))

if __name__ == "__main__":
    main()
""",
    "循环数组题把数组复制一遍再跑，不要真的修改原数组长度。")

add("二叉树", "补充篇二叉树题量最大（遍历、构造、BST、公共祖先、路径），输入统一是「n + 层序数组」，"
     "空节点写 null。建树模板和速成篇一样，区别在于输出：中序遍历要打一串数，构造类题要打整棵树的层序结果。",
    """
import sys
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build(tokens):
    if not tokens or tokens[0] in ("null", "None", "#"):
        return None
    root = TreeNode(int(tokens[0]))
    q = deque([root])
    i = 1
    while q and i < len(tokens):
        node = q.popleft()
        if i < len(tokens) and tokens[i] not in ("null", "None", "#"):
            node.left = TreeNode(int(tokens[i]))
            q.append(node.left)
        i += 1
        if i < len(tokens) and tokens[i] not in ("null", "None", "#"):
            node.right = TreeNode(int(tokens[i]))
            q.append(node.right)
        i += 1
    return root

def level_order(root):
    out, q = [], deque([root]) if root else deque()
    while q:
        node = q.popleft()
        out.append(str(node.val))
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
    return out

def main():
    sys.setrecursionlimit(10 ** 6)
    data = sys.stdin.read().split()
    root = build(data[1:])

    print(*Solution().inorderTraversal(root))     # 换成该题的方法

if __name__ == "__main__":
    main()
""",
    "输出整棵树用层序（level_order）打一行，空节点按题目要求补 null；"
    "构造类题目（106、654）输入可能给两个数组（中序 + 后序），按「先读完两个数组再建树」处理。")

add("回溯算法", "补充篇的回溯题输入是「n」「n + k」「n + 数组」或「棋盘/字符串」。"
     "解数独这类题要把 9 行棋盘按行读成 char 数组，输出时按行打回字符串。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])

    ans = Solution().combine(n, k)
    print(len(ans))
    for row in ans:
        print(*row)

if __name__ == "__main__":
    main()
""",
    "二维结果统一「先方案数，再每行一个方案」；解数独输出 9 行字符串。")

add("贪心算法", "贪心题输入是「n + 数组」或「数组 + 限制」，"
     "多数题要先按某个维度排序（身高、区间右端点、孩子胃口），排序写在方法里。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    nums = list(map(int, data[1:1 + n]))

    print(Solution().findContentChildren(nums, nums))

if __name__ == "__main__":
    main()
""",
    "区间题按「左端点排序」还是「右端点排序」结果不同，先确认题目要哪种。")

add("动态规划", "补充篇 DP 覆盖：基础（斐波那契/爬楼梯）、背包（01/完全/多重）、打家劫舍、股票、子序列。"
     "背包题输入是「物品数 n + 容量 bagweight」，然后每行「重量 价值」；读成一维数组更省事。",
    """
import sys

def main():
    data = sys.stdin.read().split()
    p = 0
    n, bag = int(data[p]), int(data[p + 1]); p += 2
    weight = list(map(int, data[p:p + n])); p += n
    value = list(map(int, data[p:p + n])); p += n

    dp = [0] * (bag + 1)
    for i in range(n):
        for j in range(bag, weight[i] - 1, -1):   # 01 背包倒序；完全背包正序
            dp[j] = max(dp[j], dp[j - weight[i]] + value[i])
    print(dp[bag])

if __name__ == "__main__":
    main()
""",
    "01 背包容量必须倒序遍历，完全背包正序——这是最容易写反的一行。")

add("图论", "补充篇图论题输入三种：① 边表「n m 然后 m 行 u v」；② 网格「m n 然后 m 行 0/1」；"
     "③ 带权「u v w」。建图时无向图要双向加边，有向图只加一次，别搞反。",
    """
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

    for _ in range(m):
        u, v = int(data[p]), int(data[p + 1]); p += 2
        ru, rv = find(u), find(v)
        if ru == rv:
            print(u, v)          # 冗余连接：这条边让图成环
            return
        parent[ru] = rv

if __name__ == "__main__":
    main()
""",
    "网格题先把每行读成字符串；带权最短路用 `heapq` 的 Dijkstra，别用 Bellman-Ford 硬算大数据。")

CHAPTER_ORDER_I = ["哈希", "双指针", "滑动窗口", "子串", "普通数组", "矩阵", "链表", "二叉树",
                   "图论", "回溯", "二分查找", "栈", "堆", "贪心算法", "动态规划", "多维动态规划", "技巧"]
CHAPTER_ORDER_II = ["数组", "链表", "哈希表", "字符串", "栈与队列", "单调栈", "二叉树",
                    "回溯算法", "贪心算法", "动态规划", "图论"]

if __name__ == "__main__":
    import json, io, sys
    sys.stdout.reconfigure(encoding="utf-8")
    io.open(r"C:\Users\31964\Desktop\leetcode\work\chapters.json", "w", encoding="utf-8").write(
        json.dumps(CH, ensure_ascii=False, indent=1))
    print("chapters:", len(CH))
    for k in CHAPTER_ORDER_I:
        assert f"1|{k}" in CH, k
    for k in CHAPTER_ORDER_II:
        assert f"2|{k}" in CH, k
    print("all chapter orders covered")
