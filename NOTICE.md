# 归属与许可

```
gzh-studio - 公众号内容全流程 skill
Copyright (C) 2026 Roloyty

本作品整体按 GNU Affero General Public License v3.0 或更高版本授权。
完整许可证文本见根目录 LICENSE。

组成部分与各自的著作权归属:

  vendor/gzh-design/     Copyright (C) 2026 甲木 (Jiamu) x 摸鱼小李 (Moyu Xiaoli)
                         AGPL-3.0。本作品因包含它而整体适用 AGPL-3.0。
  vendor/khazix-writer/  Copyright (c) 2026 数字生命卡兹克 (Khazix)   MIT
  vendor/viral-title/    Copyright (c) kangarooking                   MIT
  vendor/cover-skill/    Copyright (c) kangarooking                   MIT

MIT 部分在本作品中按其原许可证提供，各自的许可证文本保留在对应目录内。
把它们与 AGPL 部分组合而成的整体，按 AGPL-3.0 分发。
```

本 skill 是一个**编排层**。四套上游能力原样 vendored 在 `vendor/` 下，各自的 `LICENSE` 与版权声明都保留在原目录里，没有删改。

## 上游

| 目录 | 上游项目 | 作者 | 许可证 |
|------|---------|------|--------|
| `vendor/khazix-writer/` | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) 的 `khazix-writer` | 数字生命卡兹克 (Khazix) | MIT |
| `vendor/viral-title/` | [kangarooking/kangarooking-skills](https://github.com/kangarooking/kangarooking-skills) 的 `viral-title` | kangarooking | MIT |
| `vendor/cover-skill/` | [kangarooking/kangarooking-skills](https://github.com/kangarooking/kangarooking-skills) 的 `cover-skill` | kangarooking | MIT |
| `vendor/gzh-design/` | [isjiamu/gzh-design-skill](https://github.com/isjiamu/gzh-design-skill) | 甲木 (Jiamu) × 摸鱼小李 (Moyu Xiaoli) | **AGPL-3.0** |

vendored 于 2026-09-05，取各仓库当时的 `main`。

## 本仓库的许可证

`vendor/gzh-design/` 是 **AGPL-3.0**（copyleft，且覆盖网络服务场景）。本仓库把它与其余部分组合成一个整体并公开分发，因此**整体按 AGPL-3.0 授权**，包括本 skill 自己写的编排层、裁决表和脚本。根目录 `LICENSE` 是 AGPL-3.0 全文。

对使用者意味着：

- **自己拿去用、改，随便。** AGPL 不限制私人使用，也不禁止商用。
- **你再分发它**（fork 后公开、打包给别人、发到 skill 市场），得继续按 AGPL-3.0 并提供完整源码。
- **你拿它做线上服务**（比如做成网页版排版工具），AGPL 第 13 条要求你向服务的使用者提供源码——哪怕你没有分发软件本身。

MIT 部分（khazix-writer / viral-title / cover-skill）在这里按其原许可证提供，各自的版权声明和许可证文本保留在对应目录内。**如果你只想要那三个 MIT 的部分**，直接去它们的上游仓库取，不受本仓库 AGPL 的约束。

## 本 skill 自身的原创部分

`SKILL.md`、`references/`、`config/`、`scripts/` 是为串联这四套能力而写的，不是任何一方的复制：

- **章节注释锚点机制**（`<!-- sec: | tag: -->` / `lede` / `img` / `sign`）——解决卡兹克风格「正文不写小标题」与 gzh-design「靠 `##` 分章编号」的结构冲突。
- **跨阶段冲突裁决表**（`references/conflict-rules.md`）——标点禁令、加粗密度、下划线密度、bullet 禁令、签名唯一性等 20 余条互斥规则的取舍。
- **流水线产物契约**（`references/pipeline-contract.md`、`state.json`）——让阶段之间靠文件而非对话记忆交接。
- **`scripts/check_article.py`**——把 khazix-writer 的 L1 层自检做成确定性脚本，上游只有文字描述、没有脚本。
- **品牌层解耦**（`config/brand-assets.md`）——把 cover-skill 里硬绑定原作者头像与袋鼠 IP 的强制项，改成可配置资产。

## 使用边界

- **不使用 `vendor/cover-skill` 原作者的真人头像与袋鼠 IP 素材**，那不属于本 skill 的用户。封面品牌资产一律走 `config/brand-assets.md`。
- `khazix` voice preset 会写出署名「卡兹克」和其投稿邮箱的文章。**那是卡兹克本人的身份**，除非你就是他，否则用 `custom` preset 并填好 `config/author-profile.md`。以他人身份署名发布是冒名，不要这么干。
