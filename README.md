# gzh-studio

公众号内容全流程 skill。把**选题 → 写作 → 起标题 → 排版 → 封面 → 交付**串成一条流水线，一次交付可直接发布的成品。

集成了四套开源能力，每套只做它最擅长的一环：

| 阶段 | 能力来源 | 干什么 |
|------|---------|--------|
| 写作 | [khazix-writer](https://github.com/KKKKhazix/khazix-skills) | 卡兹克那套长文方法论：HKR 选题质检、写作技法、绝对禁区、四层自检 L1–L4 |
| 标题 | [viral-title](https://github.com/kangarooking/kangarooking-skills) | 10 公式 × 3 变体 = 30 个候选，打分选优，公众号专属方法论 + 爆款标题库 |
| 排版 | [gzh-design-skill](https://github.com/isjiamu/gzh-design-skill) | 6 套主题组件库，转成粘贴不掉样式的公众号 HTML，带合规校验 |
| 封面 | [cover-skill](https://github.com/kangarooking/kangarooking-skills) | 四概念探索 → 选一 → 五比例适配，21:9 公众号封面，含 QA |

## 许可证

**AGPL-3.0**。因为排版环用的 gzh-design-skill 是 AGPL-3.0，本仓库把它和其余部分组合成一个整体，整体就得按 AGPL-3.0 走——包括本 skill 自己写的编排层和裁决表。

自己拿去用和改随便，AGPL 不限制私人使用也不禁止商用；但你**再分发**或**拿它做线上服务**时，需要继续 AGPL 并提供源码。只想要 MIT 那三部分的话，直接去它们的上游仓库取。

完整归属见 [NOTICE.md](NOTICE.md)。

## 为什么不是直接装四个 skill

因为它们串起来会打架。举几个真实冲突：

- khazix 风格**正文不写小标题**，gzh-design **靠 `##` 分章做编号和目录**——直接串会把整篇当成一章。
- khazix **禁正文冒号、破折号、双引号**，gzh-design **要求全角标点**（含全角冒号破折号）、把直引号转成弯引号——两边都按自己的来，改完再改回去。
- cover-skill 的品牌层**硬绑定它作者的真人头像和袋鼠 IP**，换个人用就卡在「缺素材」上。
- viral-title 追点击率，容易起出**正文兑现不了的标题**。

本 skill 的主要价值就是这些冲突的裁决，写在 [references/conflict-rules.md](references/conflict-rules.md)。

## 装

```bash
git clone <this-repo> ~/.claude/skills/gzh-studio
```

或者把整个目录拷进 `~/.claude/skills/`（Windows 是 `C:\Users\<你>\.claude\skills\`）。

装完先配两个文件，不配也能跑，但成品里会留 `{{占位符}}`：

- [config/author-profile.md](config/author-profile.md)——署名、简介、尾部 CTA、账号口癖。**署名和 CTA 的唯一来源**，写作和排版两个阶段都从这里取。
- [config/brand-assets.md](config/brand-assets.md)——封面用的头像 / IP 形象 / Logo / 品牌色。全留空就走纯文字图形封面。

## 用

直接说人话即可，skill 会自己判断从哪一环进：

```
帮我写一篇公众号，素材在 ./材料.pdf，写完起标题、排版、做封面
把 draft.md 排版成公众号 HTML
给这篇文章起 30 个标题挑一个
做个 21:9 的公众号封面
```

## 目录

```
SKILL.md                     编排层：路由 + 六个阶段 + 硬规则
NOTICE.md                    归属与许可（含 AGPL 提醒）
references/
  conflict-rules.md          跨阶段冲突裁决表（本 skill 的核心）
  pipeline-contract.md       产物契约、state.json 结构、锚点格式
config/
  author-profile.md          作者档案（署名 / CTA 唯一来源）
  brand-assets.md            封面品牌资产
  presets/README.md          voice preset：khazix vs custom
scripts/
  new_article.py             建文章工程目录
  check_article.py           L1 硬性规则扫描器
vendor/                      四套上游 skill，原样保留各自 LICENSE
```

## 关键机制：章节注释锚点

卡兹克风格的文章正文不写小标题，但排版要靠章节做编号和目录。桥接办法是注释锚点——正文照常一口气顺下来，板块之间插一行 HTML 注释：

```markdown
<!-- lede -->
开头金句段。

<!-- sec: 事情是这样的 | tag: STORY -->
正文……

<!-- img: 后台订单页截图 -->

<!-- sec: 说点我自己的想法 | tag: THOUGHTS -->
正文……

<!-- sign -->
尾部签名区。
```

排版阶段把 `sec` 锚点渲染成主题的章节标题组件，`tag` 直接当英文标签用。**渲染结果里没有这些注释**，读者看到的仍是无小标题的顺流文章。

## 脚本

```bash
# 建工程目录
python scripts/new_article.py "文章主题"

# L1 硬性规则扫描（禁用词 / 禁用标点 / 套话 / 空泛工具名 / 锚点格式 / 加粗密度 / bullet）
python scripts/check_article.py output/<slug>/article.md --preset khazix
```

`check_article.py` 只覆盖 L1。L2 风格一致性、L3 内容质量、L4 活人感终审是判断题，仍要人工跑。

### Windows 注意

- 没有 `python3`，用 `python`。
- **调 vendor 里的脚本要带 `PYTHONUTF8=1`**，否则中文和 emoji 输出会 `UnicodeEncodeError` 崩掉：
  ```bash
  PYTHONUTF8=1 python vendor/gzh-design/scripts/validate_gzh_html.py out.html
  ```
  PowerShell 里是 `$env:PYTHONUTF8=1; python ...`。本 skill 自己的脚本已在代码里处理，不需要前缀。
