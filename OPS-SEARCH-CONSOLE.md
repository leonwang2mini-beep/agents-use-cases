# Search Console 收录观察

只读累积记录。不在本文件之外改站或推送。

## 2026-11-12（周四例行）

线上健康：`/`、`/sitemap.xml`、`/llms.txt` 均 200。生产 sitemap 98 条 `<loc>`，抽样 5 条（`/`、`/about.html`、`/use-case.html?id=coding-agents`、`/tool.html?id=cursor`、`/best/index.html`）全 200。

属性：`https://agents-use-cases.vercel.app/`

站点地图 `/sitemap.xml`：
- 状态：成功（相对 2026-10-29 记录无变化）
- 已提交日期：2026年10月28日
- 上次读取：2026年11月10日（上次记录为 10/28）
- 已发现的网页：98（上次记录 88）；已发现的视频：0
- 无错误码或警告

网页索引编制（「所有已知网页」，来源 `/sitemap.xml`）：
- 上次更新日期：2026/11/6（早于 11-09 生产发布，报告偏旧）
- 已编入索引：64
- 未编入索引：26，4 个原因
- 不再显示「正在处理数据」（2026-10-29 时仍在处理、无收录数）
- 未收录原因均于 2026/11/7 首次检测到，验证状态均为「未启动」

### 需要关注：软 404（网站，2）

- `https://agents-use-cases.vercel.app/tool.html`（上次抓取 2026年11月3日）
- `https://agents-use-cases.vercel.app/tool.html?id=composio`（上次抓取 2026年11月4日）

只读核查（HTTP 均为 200）：生产 `tool.html` 是前端渲染壳页。初始 HTML 的 title 为通用 “Tool · Agents Use Cases”，canonical 一律指向 `https://agents-use-cases.vercel.app/tool.html`（不含 `?id=`）。无 `id` 或工具未找到时，脚本写入 “Tool not found” 但响应仍是 200，且不更新 title/canonical，空壳容易被判软 404。`composio` 在生产 catalog 中存在；脚本本会在客户端把 canonical 改成带 `id` 的地址，但 Google 若只看初始 HTML，看到的仍是指向空壳的薄页。本地 11-09 每周构建已生成可爬的静态 `/tools/<id>.html`，尚未获批 push。

建议（待批准，不要自行改）：生产改用静态工具页，或在服务端输出正确 title/canonical；无 `id` 的 `/tool.html` 宜回真实 404 或 301 到目录页，不要 200 空壳。

### 备用网页（有适当的规范标记）（网站，2）——不一定要修

- `https://agents-use-cases.vercel.app/use-case.html?id=pr-changelog`（上次抓取 2026年11月4日）
- `https://agents-use-cases.vercel.app/use-case.html?id=seo-draft`（上次抓取 2026年10月28日）

这两页初始 HTML 的 canonical 指向 `https://agents-use-cases.vercel.app/use-case.html`（无 `id`）。同时已有静态 `/best/pr-changelog.html`、`/best/seo-draft.html`，且自指 canonical。Google 按规范合并，属预期表现，不是冲突错误。

### Google 系统延迟（不必改站）

已抓取 - 尚未编入索引（12）：
`/tool.html?id=kling`、`/tool.html?id=rea`、`/api/featured.json`、`/best/mcp-agent-tooling.html`、`/tool.html?id=grammarly`、`/api/rankings.json`、`/tool.html?id=modelcontextprotocol`、`/api/x-signals.json`、`/api/use-cases.json`、`/best/coding-agents.html`、`/tool.html?id=earshot`、`/best/coding-editors.html`

已发现 - 尚未编入索引（10，上次抓取均为「不适用」）：
`/api/newsletter.json`、`/api/tools.json`、`/best/browser-qa.html`、`/best/discord-bot-ops.html`、`/best/game-npc-prototyping.html`、`/tool.html?id=band`、`/tool.html?id=nitrostack`、`/tool.html?id=opencode`、`/tool.html?id=zed`、`/use-case.html?id=game-npc-prototyping`

无 4xx/5xx、被 robots 拦截或 canonical 冲突。未改站、未提交新站点地图、未推送。
