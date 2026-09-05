# 流水线产物契约

阶段之间**靠文件交接，不靠对话记忆**。中断后重入，先读 `state.json`。

## 工程目录

```
output/<slug>/
├── state.json          流水线状态，单一来源
├── brief.md            阶段 1 产出：选题结论 + 核心角度 + 板块要点
├── article.md          阶段 2 产出：正文（含章节锚点）
├── titles.md           阶段 3 产出：30 个候选 + 打分 + 选定理由
├── assets/             用户提供的素材（图片、PDF、录音转写…）
├── html/               阶段 4 产出：干净正文片段 + 预览页
└── cover/              阶段 5 产出：cover-skill 的 concepts/ 与 selected-*/
```

## state.json

```json
{
  "slug": "deepseek-9kuai9",
  "created": "2026-09-05",
  "voice_preset": "khazix",
  "theme": "moyu-green",
  "phases": {
    "topic":   "done",
    "draft":   "done",
    "title":   "done",
    "layout":  "pending",
    "cover":   "pending",
    "deliver": "pending"
  },
  "title": {
    "final": "我花9块9买了个DeepSeek，然后发现了一条产业链",
    "summary": "一次9块9的冲动消费，扒出了AI灰产的完整链路",
    "alternates": ["...", "..."]
  },
  "artifacts": {
    "brief":   "brief.md",
    "draft":   "article.md",
    "titles":  "titles.md",
    "html":    "html/xxx_排版_摸鱼绿(moyu-green).html",
    "preview": "html/xxx_排版_摸鱼绿(moyu-green)_预览.html",
    "cover":   "cover/selected-B/wechat-21x9.png"
  },
  "todos": ["尾部署名待用户替换", "第3节缺一张录屏 GIF"]
}
```

`phases` 每项取值 `pending` / `doing` / `done` / `skipped`。**完成一个阶段就更新，再往下走。**

## article.md 格式

```markdown
# 工作标题（阶段 3 完成后替换为选定标题）

<!-- lede -->
开头那段金句 / 情绪切入。

<!-- sec: 事情是这样的 | tag: STORY -->
正文……

<!-- sec: 我扒了一下这条链路 | tag: DIGGING -->
正文……

<!-- img: 后台订单页截图 -->

<!-- sec: 说点我自己的想法 | tag: THOUGHTS -->
正文……

<!-- sign -->
尾部签名区，文案取自 config/author-profile.md。
```

规则：

- 锚点独占一行，前后各留一个空行。
- 流水线只认四种锚点：`sec` / `lede` / `img` / `sign`。其余注释会被扫描器报 WARN。
- `sec` 是中文章节名，用于生成章节标题组件；`tag` 是英文标签，**必填**，排版阶段直接用，不再自己猜。
- 常用 tag：STORY / TEST / TUTORIAL / DIGGING / COMPARE / DATA / THOUGHTS / SUMMARY。
- `<!-- lede -->` 全文最多一个，标记开头引言金句段。
- `<!-- img: 说明 -->` 表示这里要配图但还没有 URL，排版阶段渲染成居中素材占位板块。有真实 URL 就直接写 `![说明](URL)`。
- `<!-- sign -->` 全文最多一个，标记尾部签名区，排版阶段把它并入唯一的签名卡。
- `custom` preset 若允许小标题，直接写 `##`，不必用锚点；两者混用时按文档顺序合并。

## titles.md 格式

```markdown
# 标题候选

## 30 个候选
（viral-title 的 10 公式 × 3 变体，原样保留）

## 打分
（viral-title 的评分表）

## 选定
**最终标题**：……
**理由**：……
**摘要（40字内，供封面用）**：……
**备选**：1. …… 2. ……
**事实核对**：逐条列出标题里的数字 / 产品名 / 结论，标明在 article.md 的哪一段兑现
```

## 交接检查

进入下一阶段前确认：

| 进入阶段 | 必须已有 |
|---------|---------|
| 2 写作 | `brief.md`、`state.json.voice_preset` |
| 3 标题 | `article.md` 完成且 `check_article.py` 零 ERROR |
| 4 排版 | `article.md` 含章节锚点（或 `##`）、`state.json.title.final` 已写回 `article.md` |
| 5 封面 | `state.json.title.final` 和 `title.summary` 都有值 |
| 6 交付 | 三个校验脚本全部零 ERROR |
