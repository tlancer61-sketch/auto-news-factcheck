# 汽车新闻真相核查

版本：v1.2.1 · Codex Skill · 中文

从消费者角度核查汽车新闻、事故争议、投诉、召回、宣传争议和官方回应。研究过程保留完整证据，正文用三个问题讲清楚：**发生什么、问题在哪、应该怎么办**。

## 工作方法

- 优先原始材料和官方来源，交叉核验关键主张，区分同源转载与独立证据。
- 从产品用途、失效后果、合理使用边界及法律义务出发给出条件判断。
- 从官方、社会与消费者、语言文法三个角度解读声明，不凭措辞推断动机。
- 区分事实、当事方说法、推断、未知，以及“应该怎样处理”和“预计怎样发展”。
- 正文先给一句结论与三个问题；详细证据、法规和分析可展开阅读。

## 安装与使用

将仓库目录复制到 Codex 的用户技能目录，并命名为 `auto-news-factcheck`。常见位置为 `~/.codex/skills/auto-news-factcheck`。如已有同名技能，先保留旧版再更新。

调用示例：

> 使用 $auto-news-factcheck 核查这则汽车新闻：[链接或内容]。先简明说明，再附完整证据。

技能会使用当前环境中可用的搜索与浏览工具；联网受限时明确说明尚未完成外部核验。

## 输出

默认生成 `report.md`、`evidence.json` 与自包含的 `explainer.html`。HTML提供简明说明和可展开的完整证据。用户只要短答时尊重其范围。

图文渲染器仅依赖 Python 3 标准库：

```bash
python3 scripts/render_explainer.py evidence.json --output explainer.html
```

输入字段见 [输出约定](references/output-contract.md)。渲染成功不代表证据真实性通过认证。

## 文件

- [SKILL.md](SKILL.md)：技能入口与流程。
- [第一性原理与处理路线](references/first-principles.md)。
- [法规与官方声明分析](references/analysis-guide.md)。
- [图文输出约定](references/output-contract.md)。
- `scripts/render_explainer.py`：本地图文渲染。
- `agents/openai.yaml`：技能展示信息。

## 边界与后续优化

不承诺还原全部事实；不替代专业鉴定或司法、监管结论。所有结论注明时间、范围与信息缺口，法律和标准在每次具体核查时核对有效版本。后续可根据真实案例继续优化。
