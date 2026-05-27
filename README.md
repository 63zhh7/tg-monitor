# TG Monitor

监控 Telegram 频道 [nanoka_news](https://t.me/nanoka_news) 的游戏更新动态，自动抓取并推送结构化更新内容。

## 功能

- 定时抓取 TG 频道消息（每天北京时间凌晨 4 点自动执行）
- 自动解析游戏更新信息，提取版本号和更新内容
- 支持的游戏：
  - 绝区零 (Zenless Zone Zero)
  - 异环 (Neverness to Everness)
  - 原神 (Genshin Impact)
  - 崩坏：星穹铁道 (Honkai: Star Rail)
  - 鸣潮 (Wuthering Waves)
- 未识别的消息原文保留，不遗漏任何内容
- 支持通过 QQ 机器人（AstrBot）以合并转发形式查看

## 文件结构

```
├── fetch_tg.py          # TG 频道抓取脚本（GitHub Actions 执行）
├── result.json          # 抓取结果缓存
├── .github/workflows/
│   └── fetch.yml        # GitHub Actions 定时任务配置
```

## 数据格式

`result.json` 结构：

```json
{
  "channel": "nanoka_news",
  "updated": "2026-05-27T03:59:02Z",
  "method": "s/nanoka_news",
  "count": 23,
  "messages": [
    {
      "time": "2026-05-25T10:49:34+00:00",
      "text": "Zenless Zone Zero updated to 3.0.4..."
    }
  ]
}
```

## 部署

### GitHub Actions（自动抓取）

1. Fork 本仓库
2. 在仓库 Settings → Secrets and variables → Actions 中添加 `TG_CHANNEL`（可选，默认 `nanoka_news`）
3. Actions 会每天北京时间凌晨 4 点自动执行抓取

### 手动触发

```bash
# 通过 GitHub API 手动触发
curl -X POST https://api.github.com/repos/你的用户名/tg-monitor/actions/workflows/fetch.yml/dispatches \
  -H "Authorization: token 你的TOKEN" \
  -d '{"ref":"main"}'
```

## 许可证

MIT
