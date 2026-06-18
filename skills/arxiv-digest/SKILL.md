---
name: arxiv-digest
description: |
  每日 arXiv AI/ML 论文推送。
  当收到 systemEvent 包含 "arxiv paper digest" 或用户要求"论文推送""今日论文""arxiv"时激活。
---

# ArXiv Paper Digest

每日获取 arXiv AI/ML 领域最新论文，生成中文摘要并推送到微信。

## 触发条件

- 定时任务 systemEvent 触发（每日早 8:00）
- 用户微信消息："今日论文""论文推送""arxiv""paper digest"

## 工作流程

### 1. 获取论文
```bash
python skills/arxiv-digest/scripts/fetch_papers.py
```
输出为 JSON（stdout），包含 `top_paper` 和 `additional_papers`。

### 2. 读取并理解结果
脚本输出 JSON，包含每篇论文的 title、authors、abstract、link、categories、cross_list_count。

### 3. 生成中文摘要
按以下模板生成 Markdown 文本：

```
arXiv AI/ML 今日速递
2026年X月X日

论文总数：N 篇
涵盖：cs.AI, cs.LG, cs.CL, cs.CV, cs.RO, stat.ML

---
### 深度解读
#### [论文标题]
**作者**：[前3位作者等]
**领域**：[交叉列出分类]
**链接**：[arxiv链接]
**核心贡献**：[用中文写约200-300字摘要：问题是什么、方法是什么、为什么重要。通俗易懂，面向AI从业者。]
---

### 更多值得关注

- ** [论文标题] ** — [一句话核心贡献] [链接]
- ** [论文标题] ** — [一句话核心贡献] [链接]
- ** [论文标题] ** — [一句话核心贡献] [链接]
- ** [论文标题] ** — [一句话核心贡献] [链接]
---
数据来源：arxiv.org RSS feeds
```

要求：
- 全中文输出，专业术语保留英文
- 深度解读选交叉列表数量最多的那篇
- 简明列表每篇用一句话概括核心贡献
- 使用 emoji 适度点缀
- 所有链接用完整的 https://arxiv.org/abs/XXXX.XXXXX 格式

### 4. 推送到微信
```bash
python skills/arxiv-digest/scripts/deliver_wechat.py --file <摘要文件路径>
```
或通过管道输入。

### 5. 保存记录
无论发送成功与否，将摘要保存到：
```
memory/arxiv-digest-YYYY-MM-DD.md
```

## 投递失败处理

如果 deliver_wechat.py 返回错误（非零退出码）：
1. 确认摘要已保存到 memory/arxiv-digest-YYYY-MM-DD.md
2. 在当天 memory/YYYY-MM-DD.md 中记录：`待发送论文摘要，下次互动时提醒`
3. 下次 Kira 在微信发消息时，主动说："之前有一期论文摘要未能推送，现在补发：[摘要内容]"

## 脚本说明

| 脚本 | 用途 | 输入 | 输出 |
|------|------|------|------|
| fetch_papers.py | 从 arXiv RSS 获取论文 | 无 | JSON (stdout) |
| deliver_wechat.py | 微信主动消息推送 | --file 或 stdin | success/error |

### fetch_papers.py 输出示例
```json
{
  "fetched_at": "2026-06-04T00:00:00Z",
  "total_fetched": 950,
  "top_paper": {
    "arxiv_id": "2606.xxxxx",
    "title": "...",
    "authors": ["..."],
    "abstract": "...",
    "link": "https://arxiv.org/abs/2606.xxxxx",
    "primary_category": "cs.AI",
    "categories": ["cs.AI", "cs.LG", "cs.CV"],
    "cross_list_count": 3,
    "published": "..."
  },
  "additional_papers": [...],
  "error": null
}
```

## 错误速查

| 情况 | 原因 | 处理 |
|------|------|------|
| total_fetched = 0 | RSS 无新论文或网络错误 | 不推送，不发"获取失败"给用户 |
| error 字段非空 | 部分分类获取失败 | 附加说明在摘要末尾 |
| deliver_wechat.py 失败 | API 不可用 | 保存文件，下次互动补发 |
