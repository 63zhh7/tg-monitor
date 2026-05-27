import requests
import json
import re
from datetime import datetime

CHANNEL = "nanoka_news"
OUTPUT_FILE = "result.json"

# 多个备选URL
URLS = [
    f"https://t.me/s/{CHANNEL}",
    f"https://t.me/{CHANNEL}",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def try_fetch(url, timeout=20):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def parse_messages(html):
    """多策略解析消息"""
    results = []

    # 策略1: 匹配 tgme_widget_message_text
    texts = re.findall(
        r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>\s*',
        html, re.DOTALL
    )
    dates = re.findall(
        r'<time[^>]*datetime="([^"]*)"',
        html
    )

    # 策略2: 匹配手机版消息
    if not texts:
        # 手机版：找 message 相关的 div
        texts = re.findall(
            r'<div class="tgme_widget_message_wrap[^>]*>.*?<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>',
            html, re.DOTALL
        )
        if not dates:
            dates = re.findall(
                r'<time datetime="([^"]+)"',
                html
            )

    # 策略3: 直接找所有带文本的 message 元素
    if not texts:
        # 匹配任何包含消息内容的块
        blocks = re.findall(
            r'<div[^>]*class="[^"]*tgme_widget_message[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>',
            html, re.DOTALL
        )
        for block in blocks[:10]:
            text = re.sub(r'<[^>]+>', ' ', block)
            text = re.sub(r'\s+', ' ', text).strip()
            dt = re.search(r'datetime="([^"]+)"', block)
            if text and len(text) > 10:
                results.append({
                    "time": dt.group(1) if dt else "",
                    "text": text[:500]
                })
        return results

    # 用策略1/2的结果
    for i, text in enumerate(texts):
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        dt = dates[i] if i < len(dates) else ""
        if text:
            results.append({"time": dt, "text": text[:500]})

    return results

def main():
    all_results = []
    method = "none"

    for url in URLS:
        print(f"🔍 Trying {url}...")
        html = try_fetch(url)
        if not html:
            continue

        # 检查是否成功获取到页面
        if "tgme_widget_message" in html or "subscriber" in html.lower() or "nanoka" in html.lower():
            results = parse_messages(html)
                # 按时间戳降序排列，确保最新的在前面
                results.sort(key=lambda x: x['time'], reverse=True)
            if results:
                method = url.replace("https://t.me/", "")
                all_results = results
                print(f"✅ Got {len(results)} messages from {method}")
                break
            else:
                print(f"⚠️ Got page but no messages parsed")
                # 保存HTML用于调试
                with open("debug.html", "w", encoding="utf-8") as f:
                    f.write(html[:5000])
                print("   Saved debug.html (first 5000 chars)")
        else:
            print(f"⚠️ Page doesn't look like Telegram channel")

    output = {
        "channel": CHANNEL,
        "updated": datetime.utcnow().isoformat() + "Z",
        "method": method,
        "count": len(all_results),
        "messages": all_results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n📦 Total: {len(all_results)} messages from {method}")

if __name__ == "__main__":
    main()