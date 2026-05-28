# TG Monitor

监控 Telegram 频道 [nanoka_news](https://t.me/nanoka_news) 的游戏更新动态，通过 AstrBot QQ 机器人自动推送。

## 功能

- 自动定时抓取 TG 频道消息（白天 8:00-22:00 每20分钟，夜间 22:00-8:00 每小时）
- 自动解析游戏更新信息，提取版本号和更新内容
- 支持的游戏：
  - 绝区零 (Zenless Zone Zero)
  - 异环 (Neverness to Everness)
  - 原神 (Genshin Impact)
  - 崩坏：星穹铁道 (Honkai: Star Rail)
  - 鸣潮 (Wuthering Waves)
- 每个游戏只显示最新一条更新动态
- 未识别的消息原文保留
- 通过 QQ 机器人以合并转发形式查看（`/tg` 命令）
- 自动检测原神/崩铁新更新，转发到指定群并 @ 群主
- `/tg_update` 手动触发抓取
- `/额度` 查看本月 GitHub Actions 剩余时间

## 架构

```
tg-monitor/
├── fetch_tg.py          # TG 频道抓取脚本
├── result.json          # 抓取结果缓存
├── main.py              # AstrBot 插件（定时触发 + 消息展示 + 自动推送）
├── .github/workflows/
│   └── fetch.yml        # GitHub Actions 配置
```

## 数据格式

```json
{
  "channel": "nanoka_news",
  "updated": "2026-05-28T10:00:00Z",
  "count": 20,
  "messages": [
    {
      "id": "8537f5ed1bef",
      "time": "2026-05-28T10:00:00+00:00",
      "text": "Genshin Impact updated to 6.7..."
    }
  ],
  "new_ids": ["8537f5ed1bef"],
  "forwarded": []
}
```

## 部署

1. Fork 本仓库
2. 配置 GitHub Secrets：`TG_CHANNEL`（可选，默认 `nanoka_news`）
3. 将 `main.py` 放入 AstrBot 插件目录
4. 修改 `main.py` 中的 `GITHUB_TOKEN`、群号、群主 QQ 号
5. AstrBot 插件内置定时器，自动触发抓取，无需依赖 GitHub Actions schedule

## 许可证

MIT
