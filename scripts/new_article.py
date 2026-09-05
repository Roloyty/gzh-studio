#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建一个文章工程目录，作为流水线各阶段的交接处。

用法:
    python3 new_article.py "文章主题或临时名" [--slug my-slug]
                           [--outdir output] [--preset khazix|custom]

产出 <outdir>/<slug>/，内含 state.json、brief.md、article.md 骨架和
assets/ html/ cover/ 三个空目录。已存在则不覆盖，直接报路径退出。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

# Windows 控制台默认 cp936，中文输出会变乱码，强制 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

PHASES = ["topic", "draft", "title", "layout", "cover", "deliver"]


def slugify(text: str) -> str:
    """ASCII 部分做 slug；中文标题没有 ASCII 可用时退回日期 + 序号。"""
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    ascii_part = re.sub(r"-{2,}", "-", ascii_part)
    if ascii_part:
        return ascii_part[:48]
    return f"article-{date.today().isoformat()}"


def unique_dir(base: Path, slug: str) -> Path:
    target = base / slug
    if not target.exists():
        return target
    for n in range(2, 100):
        candidate = base / f"{slug}-{n}"
        if not candidate.exists():
            return candidate
    raise SystemExit(f"{base} 下同名目录太多，手动指定 --slug")


BRIEF_TEMPLATE = """# 选题 brief

> 阶段 1 产出。写完再进阶段 2。

## 素材来源

-

## HKR 质检

| 维度 | 判定 | 依据 |
|------|------|------|
| H 有趣 / 有悬念 | ☐ | |
| K 有信息量 | ☐ | |
| R 有共鸣 | ☐ | |

三项兼备 = S 级；及格线是至少两项。只占一项就回去跟用户调方向，不要闷头写。

## 核心角度

一句话说清这篇要表达什么。

## 板块要点

1.
2.
3.

## 只能来自用户的东西

第一手观察、真实经历、个人判断、具体数字、真实图片 URL。**这些 AI 不许代笔编造**，缺了就问，或者在正文里留占位。

-
"""

ARTICLE_TEMPLATE = """# {title}

<!-- lede -->
开头金句 / 情绪切入段。从一个具体的、当下的事件切入，不要宏大叙事。

<!-- sec: 第一个板块的中文名 | tag: STORY -->

正文……

<!-- sec: 第二个板块的中文名 | tag: DIGGING -->

正文……

<!-- img: 这里要配一张图，写清楚配什么 -->

<!-- sec: 第三个板块的中文名 | tag: THOUGHTS -->

正文……

<!-- sign -->
尾部签名区。文案取自 config/author-profile.md，不要在这里另编一份。
排版阶段把它并入唯一的签名卡，不另起一个。
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="建文章工程目录")
    ap.add_argument("topic", help="文章主题或临时名")
    ap.add_argument("--slug", help="目录名，默认从 topic 推导")
    ap.add_argument("--outdir", type=Path, default=Path("output"))
    ap.add_argument("--preset", choices=["khazix", "custom"], default=None,
                    help="voice preset，不给就留 null，写作阶段再问用户")
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    slug = args.slug or slugify(args.topic)
    root = unique_dir(args.outdir, slug)

    for sub in ("assets", "html", "cover"):
        (root / sub).mkdir(parents=True)

    (root / "brief.md").write_text(BRIEF_TEMPLATE, encoding="utf-8")
    (root / "article.md").write_text(
        ARTICLE_TEMPLATE.format(title=args.topic), encoding="utf-8"
    )

    state = {
        "slug": root.name,
        "topic": args.topic,
        "created": date.today().isoformat(),
        "voice_preset": args.preset,
        "theme": None,
        "phases": {p: "pending" for p in PHASES},
        "title": {"final": None, "summary": None, "alternates": []},
        "artifacts": {
            "brief": "brief.md",
            "draft": "article.md",
            "titles": None,
            "html": None,
            "preview": None,
            "cover": None,
        },
        "todos": [],
    }
    state["phases"]["topic"] = "doing"
    (root / "state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"工程目录已建: {root}")
    print()
    print("接下来:")
    print(f"  1. 填 {root / 'brief.md'}，过 HKR 质检")
    print(f"  2. 定 voice preset，写进 {root / 'state.json'} 的 voice_preset")
    print(f"  3. 写 {root / 'article.md'}，别忘了埋 <!-- sec: --> 锚点")
    print(f"  4. python3 scripts/check_article.py {root / 'article.md'}")
    print()
    print("每完成一个阶段就更新 state.json 的 phases 字段再往下走。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
