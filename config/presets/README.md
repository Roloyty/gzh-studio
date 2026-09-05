# Voice Preset

写作阶段开始前**必须选一个**（用户已指明或 `state.json.voice_preset` 已有值时不用再问）。

两套共用同一份方法论骨架：HKR 选题质检、AI 角色边界、写作技法（人物画像法、文化升维、句式断裂、回环呼应、谦逊铺垫、读者直呼、层层剥开、英雄之旅、反向论证、升番逻辑）、绝对禁区、开头必杀技、四层自检 L1–L4。骨架在 `vendor/khazix-writer/SKILL.md`，别重写。

差异只在**身份层**：

| 维度 | `khazix` | `custom` |
|------|----------|----------|
| 署名 | 卡兹克 | `config/author-profile.md` 的 `{{作者名}}` |
| 公众号 | 数字生命卡兹克 | `author-profile.md` 的 `{{公众号名}}` |
| 一句话简介 | 激发大家对 AI 的好奇 | `author-profile.md` |
| 尾部 CTA | 卡兹克原版（含 wzglyay@virxact.com） | `author-profile.md` 的尾部模板 |
| 口癖词库 | `vendor/khazix-writer/SKILL.md` 的推荐口语化词组全套 | `author-profile.md` 的账号专属口癖优先；留空则退回通用词库 |
| 额外禁忌 | 无 | `author-profile.md` 的禁忌清单 |
| 小标题 | 不加，用 `<!-- sec: -->` 锚点 | 默认同 khazix；账号习惯用小标题就直接写 `##` |
| 语言禁令（冒号 / 破折号 / 双引号） | 生效 | 默认生效，可在 `author-profile.md` 的禁忌里改 |

## 选哪个

- 用户就是卡兹克本人，或明说「用卡兹克的风格」→ `khazix`
- 其余一律 `custom`，并先确认 `author-profile.md` 填过了。**全是占位符就先提醒用户填**，别直接开写然后交付一篇满是 `{{作者名}}` 的稿子。

## 加新 preset

在本目录建 `voice-<名字>.md`，只写身份层差异（上表那几行），不要复制方法论骨架。然后在上表加一列。
