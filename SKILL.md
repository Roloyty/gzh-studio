---
name: gzh-studio
description: |
  公众号内容全流程 skill，把选题、写作、起标题、排版、做封面串成一条流水线，一次交付可直接发布的成品。
  触发场景：用户说「写一篇公众号」「公众号从头做一篇」「帮我出一篇稿子并排版」「写完顺便做个封面」「公众号全流程」「出稿+标题+排版+封面」，
  或者用户给了素材（PDF / 链接 / brief / 语音转文字 / 散乱想法）说「做成一篇公众号文章」。
  也支持只跑其中一环：只写稿、只起标题、只排版、只做封面。
  不用于小红书 / 推特 / 朋友圈等短内容，不用于生成普通网页 / 落地页 / PPT。
---

# 公众号内容 Studio

这是一个**编排层**。四套上游能力已经 vendored 在 `vendor/` 下，本文件不重复它们的方法论，只负责三件事：

1. **路由**——判断用户要跑整条流水线还是其中一环。
2. **衔接**——定义每个阶段的产物契约，让下一阶段能确定性地接住上一阶段。
3. **裁决**——四套 skill 的规则互相冲突时，谁让谁（这是本 skill 存在的主要理由，见 [references/conflict-rules.md](references/conflict-rules.md)）。

| 阶段 | 能力来源 | 许可证 |
|------|---------|--------|
| 写作 | `vendor/khazix-writer/` | MIT |
| 标题 | `vendor/viral-title/` | MIT |
| 排版 | `vendor/gzh-design/` | AGPL-3.0 |
| 封面 | `vendor/cover-skill/` | MIT |

归属与许可见 [NOTICE.md](NOTICE.md)。

## 运行环境

跑任何脚本之前先看这三条，四个 vendor skill 都是在类 Unix 环境下写的，直接照抄它们的命令在 Windows 上会挂。

1. **没有 `python3`，只有 `python`。** 本文件和 vendor 各 SKILL.md 里的 `python3 xxx.py` 一律换成 `python xxx.py`，否则 command not found。
2. **vendor 脚本必须带 `PYTHONUTF8=1`。** 它们往 stdout 打中文和 emoji，Windows 默认 cp936，不带这个环境变量会直接 `UnicodeEncodeError` 崩掉——`validate_gzh_html.py` 是排版阶段的强制闸门，崩了就等于跳过了校验。
   ```bash
   PYTHONUTF8=1 python vendor/gzh-design/scripts/validate_gzh_html.py <file>
   ```
   PowerShell 里写成 `$env:PYTHONUTF8=1; python ...`。
   本 skill 自己的 `scripts/*.py` 已经在代码里强制了 UTF-8，不需要这个前缀。
3. **vendor 里的相对路径是相对它自己目录的。** vendor 的 SKILL.md 写 `references/xxx.md`、`scripts/xxx.py` 时，实际要拼成 `vendor/<skill>/references/xxx.md`。

`<SKILL_ROOT>` 指本 SKILL.md 所在目录。

## 阶段路由

先判断用户要什么，不要默认整条跑完。

| 用户说 | 从哪进 | 跑到哪 |
|--------|--------|--------|
| 「写一篇公众号」「从头做一篇」「全流程」 | 阶段 0 | 阶段 6 |
| 「帮我写篇文章」「按我风格写」（没提排版封面） | 阶段 1 | 阶段 2，然后**问一句**要不要继续起标题/排版/封面 |
| 「给这篇起个标题」「标题不好换一批」 | 阶段 3 | 阶段 3 |
| 「把这篇排版了」「转成公众号 HTML」 | 阶段 4 | 阶段 4 |
| 「做个封面」 | 阶段 5 | 阶段 5 |
| 给了一篇已完成的稿子说「后面的都办了」 | 阶段 3 | 阶段 6 |

**单环调用时**，直接读该阶段对应的 vendor SKILL.md 按它的流程走，同时仍要遵守 [references/conflict-rules.md](references/conflict-rules.md)——因为产物随时可能被后续阶段接手。

## 阶段 0：建工程目录

整条流水线跑之前**必须先建工程目录**，否则阶段之间无法交接。

```bash
python <SKILL_ROOT>/scripts/new_article.py "<文章主题或临时名>"
```

产出 `output/<slug>/`，内含 `state.json`（流水线状态单一来源）、`brief.md`、`assets/`。
后续每完成一个阶段，**更新 `state.json` 对应字段**再往下走。产物契约与 `state.json` 字段定义见 [references/pipeline-contract.md](references/pipeline-contract.md)。

单环调用（只排版 / 只做封面）不需要建工程目录，就地产出即可。

## 阶段 1：选题与素材

读 `vendor/khazix-writer/SKILL.md` 的「第一步」和「第二步」。要点：

- 素材过 **HKR 质检**（Happy 有趣 / Knowledge 有信息量 / Resonance 有共鸣）。S 级三项兼备，及格至少两项。只占一项就主动跟用户调方向，不要闷头写。
- 素材信息不够就问用户要——想讲哪几个点、有没有亲身经历、有没有特别兴奋或特别想吐槽的地方。
- **守住 AI 的角色边界**：第一手观察、真实经历、个人判断必须来自用户；找证据、找类比、补背景、扩写、梳理结构才是 AI 该做的。没有真实细节就别硬编假设性例子。

把选题结论、核心角度、板块要点写进 `brief.md`。

## 阶段 2：写作

### 2.1 先定 voice preset

**每次写作前问一句用哪套人格**（除非用户已经指明，或 `state.json` 里已有 `voice_preset`）：

- `khazix`——数字生命卡兹克原版风格，含它的固定尾部署名和邮箱。资产：`vendor/khazix-writer/`。
- `custom`——保留卡兹克那套方法论骨架，但署名 / 简介 / 口癖词库 / 尾部 CTA 全部取自 [config/author-profile.md](config/author-profile.md)。

用 AskUserQuestion 一次问清，写进 `state.json.voice_preset`。preset 差异的完整定义见 [config/presets/README.md](config/presets/README.md)。

### 2.2 写

读 `vendor/khazix-writer/SKILL.md` 的「第三步」（写作技法、绝对禁区、口语化词组、开头必杀技、升番逻辑、结构模板）和 `references/content_methodology.md`、`references/style_examples.md`。

`custom` preset 下，方法论骨架照用，但这几处换成 `author-profile.md` 的内容：署名、一句话简介、尾部三连 CTA、投稿联系方式、账号专属口癖词。**`author-profile.md` 里是 `{{占位符}}` 的字段，就保留占位符交付并提示用户替换，绝不自己编一个名字。**

### 2.3 埋章节锚点（关键，别跳过）

卡兹克风格**正文不写小标题**，但排版阶段要靠章节做编号、目录和标题组件。桥接办法是**注释锚点**：正文照常一口气顺下来，在每个语义板块开始的空行处插入一行 HTML 注释——

```markdown
<!-- sec: 我为什么去买了个9.9的号 | tag: STORY -->
```

- `sec` 是中文章节名，排版阶段拿它生成章节标题组件；`tag` 是英文标签（实测→TEST、教程→TUTORIAL、总结→SUMMARY、思考→THOUGHTS…），省掉排版阶段自己猜。
- 开头引言金句段前加 `<!-- lede -->`，全文最多一个。
- 需要配图的位置写 `<!-- img: 说明文字 -->`；有真实图片 URL 时才写标准 markdown 图片语法。
- 尾部签名区前加 `<!-- sign -->`，全文最多一个，排版阶段据它并入唯一的签名卡。
- 流水线只认这四种锚点，别自创第五种。
- 注释锚点**不出现在渲染结果里**，公众号读者看到的仍是无小标题的顺流文章——排版阶段会把锚点替换成主题的章节标题组件。

`custom` preset 如果允许小标题，直接写 `##` 即可，不必用锚点。

### 2.4 四层自检 + 脚本扫描

先跑确定性扫描，把 L1 硬性规则的漏网之鱼捞干净：

```bash
python <SKILL_ROOT>/scripts/check_article.py output/<slug>/article.md --preset khazix
```

它检查禁用词、禁用标点、结构套话、空泛工具名、锚点格式、加粗密度。**ERROR 清零才算过 L1。**
然后按 `vendor/khazix-writer/SKILL.md`「第四步」人工跑完 L2 风格一致性、L3 内容质量、L4 活人感终审，输出质检报告。

脚本只覆盖 L1；L2–L4 是判断题，**不要拿脚本通过当作全部通过**。

## 阶段 3：标题

读 `vendor/viral-title/SKILL.md`，平台固定为公众号，加载 `vendor/viral-title/references/platforms/wechat-public-account.md`。

- Phase 1 必须生成 **30 个候选**（10 个通用公式 × 3 变体），再按评分表打分、选出最佳一个并说明理由。
- 需要复用标题库时用它的检索脚本，不要整份加载：
  ```bash
  PYTHONUTF8=1 python <SKILL_ROOT>/vendor/viral-title/scripts/retrieve_title_examples.py --platform wechat --query "<主题关键词>" --limit 10
  ```
- **标题的事实约束来自正文**——数字、产品名、结论都必须在 `article.md` 里真实存在，不许为了点击率造一个正文兑现不了的承诺。
- 顺手产出**一句话摘要（40 字内）**，封面阶段要用。

选定标题 + 摘要写进 `state.json.title`，并同步到 `article.md` 顶部的 `# 标题` 行。

按 viral-title 的约定，在标题响应末尾附它的反馈勾子；用户给了选择或修改就用 `scripts/log_feedback.py` 记一笔。

## 阶段 4：排版

读 `vendor/gzh-design/SKILL.md`，主题从 `vendor/gzh-design/references/theme-index.md` 选。**注意三处本 skill 的覆盖**：

1. **章节来源**：不要只找 `##`。先扫 `<!-- sec: X | tag: Y -->` 锚点，把每个锚点当作一个 `##` 章节处理，英文标签直接用锚点里的 `tag`，不要自己再猜。锚点和 `##` 同时存在时按文档顺序合并。
2. **标点裁决**：gzh-design 要求全角标点，khazix 禁正文冒号 / 破折号 / 双引号。**正文层服从 khazix 禁令**，组件层（章节标题、标签、代码块、签名卡）不受禁令约束。校验脚本报的半角标点仍要清零，但双引号一律改成「」而不是弯引号。完整裁决表见 [references/conflict-rules.md](references/conflict-rules.md)。
3. **签名区**：`{{作者名}}` 占位不要自己填，从 [config/author-profile.md](config/author-profile.md) 取；配置里还是占位符就保留占位符并在交付时提示。原文末尾已有签名段就并入唯一的签名卡，不要生成两份。

其余照 gzh-design 原流程：解析结构 → 判定文章类型 → 按主题配方装配组件 → 校验 → 输出。

**校验是强制的**，ERROR 和半角标点 WARNING 都要清零：

```bash
PYTHONUTF8=1 python <SKILL_ROOT>/vendor/gzh-design/scripts/validate_gzh_html.py <生成的.html>
PYTHONUTF8=1 python <SKILL_ROOT>/vendor/gzh-design/scripts/wrap_preview.py <生成的.html>
```

产物：干净正文片段 HTML（纯 `<section>`，不带 `<!DOCTYPE>`/`<html>`/`<body>`）+ 带「复制到公众号」按钮的预览页。

## 阶段 5：封面

读 `vendor/cover-skill/SKILL.md`、`references/core-rules.md`、`references/qa.md`。**品牌层用本 skill 的配置替换掉它的硬绑定**：

先读 [config/brand-assets.md](config/brand-assets.md)，按里面填了什么决定走哪条路：

| 配置状态 | 走法 |
|---------|------|
| 填了头像 / IP 形象 / Logo 路径 | 按 `brand-assets.md` 的规则当作必须出现的品牌元素，参照 `vendor/cover-skill/references/personal-brand.md` 的**手法**（形象一致性、正中构图、文字与主体的景深关系、Logo 确定性合成），但形象换成配置里的 |
| 只填了 Logo / 只填了配色字体 | 品牌元素只保留填了的那部分，其余按通用封面处理 |
| 全是占位符（没配置） | **跳过 personal-brand.md 的全部强制项**，走纯文字 + 图形封面，仍保留 core-rules 的质量红线和 qa 的验收 |

**不管走哪条，这些照原样保留**：

- 标题和摘要**逐字来自阶段 3**，标点空格英文大小写都不许改。
- 公众号封面比例锁 **21:9（2100×900）**，这是 cover-skill Intake 第 7 条对公众号的映射，不要回落到 16:9。
- **四概念探索 → 用户选一 → 五比例适配**两段式不能省，不要一上来就铺开所有比例。
- 中文文字、数字、真实 Logo 用确定性合成（Pillow / SVG / HTML 渲染），**不要让图像模型画中文和 Logo**。图像模型只负责场景、氛围、材质、背景扩展。
- 每张导出图都要用看图能力实际检查过再报 PASS，manifest 里的布尔值不能替代目视 QA。
- 跑导出校验：
  ```bash
  PYTHONUTF8=1 python <SKILL_ROOT>/vendor/cover-skill/scripts/validate_exports.py --phase concepts --dir <concepts-dir>
  ```

**没有可用图像生成工具时**：不要假装生成。改走纯合成路线——用 HTML/SVG 排一版 21:9 文字封面（标题 + 摘要 + 品牌色块），照样跑四概念选一和 QA，并明确告诉用户这是无图像模型的降级方案。本机可用的图像能力可以先看 `bailian-cli` skill。

## 阶段 6：交付

一次性给全，不要挤牙膏：

1. **标题**——选定的那个，附 2 个备选。
2. **封面**——21:9 主图路径 + 其余比例目录。
3. **正文**——预览页路径（告诉用户：浏览器打开 → 点右上角「复制到公众号」→ 编辑器 Ctrl/⌘+V），干净正文 HTML 路径作兜底。
4. **质检结论**——L1–L4 报告 + `validate_gzh_html.py` 结论 + 封面 QA 结论。
5. **待办**——所有 `{{占位符}}`、`<!-- img: -->` 待补图位置、需要用户替换的署名，列成清单。

最后更新 `state.json`，标记 `phases.deliver = "done"`。

## 硬规则

- **不许跳校验**。`check_article.py`、`validate_gzh_html.py`、`validate_exports.py` 三个脚本是流水线的闸门，ERROR 不清零不交付。
- **不许编事实**。人名、数字、产品名、亲身经历、图片 URL、引用出处——素材里没有就问用户或留占位，绝不填一个看起来合理的。
- **不许跨主题混用组件**。一篇文章只用所选主题 + gzh-design 通用增量库。
- **署名只有一个来源**，就是 `config/author-profile.md`。写作阶段和排版阶段不许各写各的。
- **标题只有一个来源**，就是阶段 3 的选定结果。写作阶段可以有工作标题，但最终标题以阶段 3 为准。
- **阶段之间靠 `state.json` 交接**，不靠对话记忆。中断后重入先读 `state.json`。

## Gotchas

- **锚点漏埋**：卡兹克 preset 下正文没有 `##`，锚点也没埋，排版阶段就会把整篇当一章，编号和目录全废。写完立刻 `check_article.py` 会报出来。
- **标点在阶段之间被改回去**：排版阶段做「全角化」时很容易把「」又换成弯引号、把逗号换回冒号。裁决表是单向的——正文层永远听 khazix 的。
- **签名重复**：写作阶段写了尾部 CTA，排版阶段又生成一个签名卡，成品出现两段「点赞在看转发」。排版时识别并并入，只留一处。
- **封面比例回落**：cover-skill 不带平台参数时默认 16:9，公众号必须显式锁 21:9。
- **标题承诺正文兑现不了**：viral-title 追求点击率，容易起出正文没写的承诺。选定前对着 `article.md` 核一遍。
- **下划线过密**：gzh-design 说「每个正文段落 1–3 处」，但卡兹克风格常常一句话一段，逐段标会糊成一片。改为按语义板块标，密度参考裁决表。
- **占位图残留**：签名卡 / CTA 组件里带名片图占位的，没有真实 URL 就整行删掉，别把占位符发出去。
- **vendor 里的路径**：vendor 各 SKILL.md 写的 `references/xxx.md` 是**相对它自己目录**的，读的时候要拼上 `vendor/<skill>/`。
