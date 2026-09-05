#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""article.md 的 L1 硬性规则扫描器。

自动化 vendor/khazix-writer 四层自检里的 L1 层（禁用词 / 禁用标点 / 结构套话 /
空泛工具名），外加本 skill 的锚点契约、加粗密度、bullet 禁令、占位符检查。

只覆盖 L1。L2 风格一致性、L3 内容质量、L4 活人感终审是判断题，仍要人工跑。

用法:
    python3 check_article.py <article.md> [--preset khazix|custom] [--quiet]

退出码: 0 = 零 ERROR; 1 = 有 ERROR; 2 = 参数或文件错误。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Windows 控制台默认 cp936，中文输出会变乱码，强制 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- 规则表

# L1-1 禁用词。命中即 ERROR，附推荐替换。
BANNED_WORDS = {
    "说白了": "坦率的讲 / 其实就是",
    "这意味着": "那结果会怎样呢 / 所以呢",
    "意味着什么": "那结果会怎样呢",
    "本质上": "说到底 / 其实",
    "换句话说": "你想想看 / 也就是说",
    "不可否认": "删掉，改成正面陈述",
    "综上所述": "换成具体的回扣句",
    "总的来说": "换成具体的回扣句",
    "值得注意的是": "删掉，直接说",
    "不难发现": "删掉，直接说",
    "让我们来看看": "删掉，直接说",
    "接下来让我们": "用口语化转场句",
}

# 上下文相关，报 WARN 让人自己判断。
SOFT_WORDS = {
    "首先": "「首先…其次…最后」是套话结构，单独用可以，成组出现要改",
    "其次": "同上",
}

# L1-3 结构性套话
CLICHE_PATTERNS = [
    (re.compile(r"在当今.{0,10}?时代"), "教科书式开头"),
    (re.compile(r"随着.{0,12}?的(发展|进步|普及)"), "教科书式开头"),
    (re.compile(r"随着.{0,12}?不断"), "教科书式开头"),
]

# L1-4 空泛工具名
VAGUE_TOOLS = ["AI工具", "AI 工具", "某个模型", "某款AI", "某款 AI", "相关技术", "一些AI", "一些 AI"]

# L1-2 禁用标点（正文层，组件层豁免）
BANNED_PUNCT = [
    ("：", "全角冒号", "用逗号代替"),
    (":", "半角冒号", "用逗号代替"),
    ("——", "破折号", "用逗号或句号代替"),
    ('"', "直双引号", "用「」代替"),
    ("“", "左弯引号", "用「」代替"),
    ("”", "右弯引号", "用「」代替"),
]

MAX_BOLD_SPANS = 5
MAX_BOLD_LEN = 10
WORDCOUNT_MIN = 4000
WORDCOUNT_MAX = 8000

ANCHOR_SEC = re.compile(r"^<!--\s*sec:\s*(.+?)\s*\|\s*tag:\s*([A-Za-z_]+)\s*-->\s*$")
ANCHOR_LEDE = re.compile(r"^<!--\s*lede\s*-->\s*$")
ANCHOR_IMG = re.compile(r"^<!--\s*img:\s*(.+?)\s*-->\s*$")
ANCHOR_SIGN = re.compile(r"^<!--\s*sign\s*-->\s*$")
ANY_COMMENT = re.compile(r"^<!--.*-->\s*$")
URL_RE = re.compile(r"(https?://\S+|www\.\S+|\S+@\S+\.\S+)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")
CJK_RE = re.compile(r"[一-鿿]")


class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[int, str, str]] = []
        self.warns: list[tuple[int, str, str]] = []

    def error(self, line: int, rule: str, msg: str) -> None:
        self.errors.append((line, rule, msg))

    def warn(self, line: int, rule: str, msg: str) -> None:
        self.warns.append((line, rule, msg))


def mask_line(raw: str) -> str:
    """把不受正文规则约束的部分抹成空格，保持列宽以便定位。

    豁免：行内代码、URL / 邮箱、HTML 注释锚点、标题行（组件层）。
    """
    if raw.lstrip().startswith("#"):
        return " " * len(raw)
    if ANY_COMMENT.match(raw.strip()):
        return " " * len(raw)
    masked = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), raw)
    masked = URL_RE.sub(lambda m: " " * len(m.group(0)), masked)
    return masked


def scan(path: Path, preset: str) -> Report:
    rep = Report()
    lines = path.read_text(encoding="utf-8").splitlines()

    in_fence = False
    body_chars = 0
    bold_spans: list[tuple[int, str]] = []
    sec_anchors: list[tuple[int, str, str]] = []
    lede_count = 0
    sign_count = 0
    heading_count = 0
    seen_tags: dict[str, int] = {}

    for no, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        # 围栏代码块整体豁免
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # ---- 锚点契约
        if stripped.startswith("<!--"):
            m = ANCHOR_SEC.match(stripped)
            if m:
                name, tag = m.group(1), m.group(2).upper()
                sec_anchors.append((no, name, tag))
                if tag in seen_tags:
                    rep.warn(no, "ANCHOR", f"tag {tag} 与第 {seen_tags[tag]} 行重复，英文标签建议每章不同")
                seen_tags[tag] = no
            elif ANCHOR_LEDE.match(stripped):
                lede_count += 1
            elif ANCHOR_IMG.match(stripped):
                pass
            elif ANCHOR_SIGN.match(stripped):
                sign_count += 1
            elif ANY_COMMENT.match(stripped):
                if "sec" in stripped or "tag" in stripped:
                    rep.error(no, "ANCHOR", f"章节锚点格式错误，应为 <!-- sec: 中文名 | tag: EN --> 实际: {stripped}")
                else:
                    rep.warn(no, "ANCHOR", f"无法识别的注释，流水线只认 sec / lede / img / sign 四种: {stripped}")
            continue

        if stripped.startswith("#"):
            heading_count += 1
            continue

        masked = mask_line(raw)
        body_chars += len(CJK_RE.findall(masked))

        # ---- L1-1 禁用词
        for word, fix in BANNED_WORDS.items():
            start = 0
            while True:
                idx = masked.find(word, start)
                if idx == -1:
                    break
                rep.error(no, "L1-1", f"禁用词「{word}」(第 {idx + 1} 列) → {fix}")
                start = idx + len(word)

        for word, note in SOFT_WORDS.items():
            if word in masked:
                rep.warn(no, "L1-1", f"套话嫌疑「{word}」 → {note}")

        # ---- L1-2 禁用标点
        for ch, name, fix in BANNED_PUNCT:
            start = 0
            while True:
                idx = masked.find(ch, start)
                if idx == -1:
                    break
                rep.error(no, "L1-2", f"禁用标点 {name}「{ch}」(第 {idx + 1} 列) → {fix}")
                start = idx + len(ch)

        # ---- L1-3 结构套话
        for pat, label in CLICHE_PATTERNS:
            m2 = pat.search(masked)
            if m2:
                rep.error(no, "L1-3", f"{label}「{m2.group(0)}」→ 从一个具体的、当下的事件切入")

        # ---- L1-4 空泛工具名
        for vague in VAGUE_TOOLS:
            if vague in masked:
                rep.error(no, "L1-4", f"空泛工具名「{vague}」→ 换成具体产品名")

        # ---- bullet 禁令（裁决表 A7）
        if preset == "khazix" and re.match(r"^\s*[-*+]\s+\S", raw):
            rep.error(no, "A7", "正文出现 bullet 列表 → 改成散文或文中数字编号（1、2、3）")

        # ---- 加粗密度（裁决表 A5）
        for m3 in BOLD_RE.finditer(masked):
            bold_spans.append((no, m3.group(1)))

        # ---- 占位符
        for m4 in PLACEHOLDER_RE.finditer(raw):
            rep.warn(no, "TODO", f"占位符 {m4.group(0)} 待替换")

    # ---- 全文级检查
    if in_fence:
        rep.error(len(lines), "FENCE", "围栏代码块没有闭合")

    if preset == "khazix" and not sec_anchors and heading_count <= 1:
        rep.error(0, "A1", "既没有 <!-- sec: --> 锚点也没有 ## 小标题，排版阶段会把整篇当一章，编号和目录全废")

    if lede_count > 1:
        rep.error(0, "ANCHOR", f"<!-- lede --> 出现 {lede_count} 次，全文最多一个")

    if sign_count > 1:
        rep.error(0, "A8", f"<!-- sign --> 出现 {sign_count} 次，签名区有且仅有末尾一处")

    for no, name, tag in sec_anchors:
        if not name.strip():
            rep.error(no, "ANCHOR", "章节锚点的中文名为空")

    if len(bold_spans) > MAX_BOLD_SPANS:
        detail = "、".join(f"L{n}:{t[:8]}" for n, t in bold_spans[:8])
        rep.error(0, "A5", f"加粗 {len(bold_spans)} 处，上限 {MAX_BOLD_SPANS} 处 → {detail}")
    for no, text in bold_spans:
        if len(text) > MAX_BOLD_LEN:
            rep.error(no, "A5", f"加粗片段 {len(text)} 字，上限 {MAX_BOLD_LEN} 字: {text[:20]}…")

    if body_chars and not (WORDCOUNT_MIN <= body_chars <= WORDCOUNT_MAX):
        rep.warn(0, "A9", f"正文约 {body_chars} 字，公众号长文建议 {WORDCOUNT_MIN}-{WORDCOUNT_MAX} 字")

    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description="article.md L1 硬性规则扫描")
    ap.add_argument("article", type=Path)
    ap.add_argument("--preset", choices=["khazix", "custom"], default="khazix")
    ap.add_argument("--quiet", action="store_true", help="只输出 ERROR")
    args = ap.parse_args()

    if not args.article.is_file():
        print(f"找不到文件: {args.article}", file=sys.stderr)
        return 2

    rep = scan(args.article, args.preset)

    def emit(items: list[tuple[int, str, str]], level: str) -> None:
        for line, rule, msg in sorted(items, key=lambda x: x[0]):
            loc = f"{args.article}:{line}" if line else str(args.article)
            print(f"{level} [{rule}] {loc}  {msg}")

    emit(rep.errors, "ERROR")
    if not args.quiet:
        emit(rep.warns, "WARN ")

    print()
    print(f"L1 扫描完成 preset={args.preset}  ERROR {len(rep.errors)}  WARN {len(rep.warns)}")
    if rep.errors:
        print("ERROR 未清零，不能进入下一阶段。")
    else:
        print("L1 通过。L2 风格一致性 / L3 内容质量 / L4 活人感终审仍需人工跑完。")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
