# TG Monitor

监控 Telegram 频道 [nanoka_news](https://t.me/nanoka_news) 的游戏更新动态，通过 AstrBot QQ 机器人自动推送。

## 功能

- 自动定时抓取 TG 频道消息（每 5 分钟触发一次 GitHub Actions）
- 自动解析游戏更新信息，提取版本号和更新内容
- 支持的游戏：
  - 绝区零 (Zenless Zone Zero)
  - 异环 (Neverness to Everness)
  - 原神 (Genshin Impact)
  - 崩坏：星穹铁道 (Honkai: Star Rail)
  - 鸣潮 (Wuthering Waves)
- 每个游戏只显示最新一条更新动态
- 未识别的消息原文保留
- 自动检测原神/星铁新更新，转发到指定 QQ 群并 @ 群主
- 通过 QQ 机器人以合并转发形式查看（`/tg` 命令）
- `/tg_update` 手动触发抓取
- 本地缓存已转发消息 ID，避免重复推送

## 指令

| 指令 | 说明 | 权限 |
| --- | --- | --- |
| `/tg` | 查看最近 7 天的游戏更新（合并转发） | 仅限指定 QQ |
| `/tg_update` | 手动触发 GitHub Actions 抓取最新数据 | 仅限指定 QQ |

## 架构

```
tg-monitor/
├── fetch_tg.py              # TG 频道抓取脚本（由 GitHub Actions 运行）
├── result.json              # 抓取结果缓存（自动更新）
├── main.py                  # AstrBot 插件（定时触发 + 消息展示 + 自动推送）
├── tg_forwarded.json        # 已转发消息 ID 缓存（自动生成）
├── metadata.yaml            # AstrBot 插件元数据
├── .github/workflows/
│   └── fetch.yml            # GitHub Actions 定时抓取配置
└── LICENSE
```

## 工作流程

1. GitHub Actions 定时运行 `fetch_tg.py`，从 TG 频道抓取最新消息，保存为 `result.json`
2. AstrBot 插件 `_auto_trigger_fetch` 每 5 分钟自动触发一次 GitHub Actions
3. 插件 `_auto_push_loop` 每 2 分钟检查 `result.json`，发现原神/星铁新更新则自动推送到 QQ 群
4. 用户可通过 `/tg` 命令手动查看最近 7 天的更新（合并转发形式）

## 配置

修改 `main.py` 中的以下配置：

| 配置项 | 说明 | 默认值 |
| --- | --- | --- |
| `GITHUB_TOKEN` | GitHub Personal Access Token | 硬编码（建议改为环境变量） |
| `GITHUB_OWNER` | GitHub 用户名 | `63zhh7` |
| `GITHUB_REPO` | 仓库名 | `tg-monitor` |
| `target_games` | 自动推送的游戏列表 | `["Genshin Impact", "Honkai: Star Rail"]` |
| 推送群号 | `_send_group_msg` 中的 `session_id` | `744822786` |
| 平台实例 ID | `_send_group_msg` 中的 `pid` | `default2`（优先）/ `default`（备选） |
| 管理员 QQ | 指令权限校验 | `1663755788` |

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
  "new_ids": ["8537f5ed1bef"]
}
```

## 部署

1. Fork 本仓库
2. 配置 GitHub Secrets：`TG_CHANNEL`（可选，默认 `nanoka_news`）
3. 将 `main.py` 放入 AstrBot 插件目录
4. 修改 `main.py` 中的 `GITHUB_TOKEN`、群号、群主 QQ 号、平台实例 ID
5. 重启 AstrBot 使插件生效

> **注意：** 插件内置定时器会自动触发 GitHub Actions 抓取，无需额外配置 Actions schedule。但需要确保 `fetch.yml` 已存在于仓库中。

## 更新日志

- **v1.1.0** — 合并转发展示、自动推送原神/星铁更新、本地缓存去重
- **v1.1.1** — 修复平台实例 ID 获取问题，支持多 aiocqhttp 实例自动选择

## 许可证

MIT
