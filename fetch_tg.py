import requests
import json
import re
from datetime import datetime

CHANNEL = "nanoka_news"
OUTPUT_FILE = "result.json"

URLS = [
    f"https://t.me/s/{CHANNEL}",
    f"https://t.me/{CHANNEL}",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}

def try_fetch(url, timeout=20):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def parse_messages(html):
    results = []
    # 寻找每一个消息块
    # TG 的 HTML 结构通常是每个消息在一个 div.tgme_widget_message_wrap 里
    blocks = re.findall(r'<div class="tgme_widget_message_wrap[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
    
    if not blocks:
        # 如果没找到 wrap，尝试找 message 块
        blocks = re.findall(r'<div[^>]*class="[^"]*tgme_widget_message[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)

    for block in blocks:
        # 提取文本
        text_match = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL)
        if not text_match:
            continue
        
        text = text_match.group(1)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 提取时间
        time_match = re.search(r'<time[^>]*datetime="([^"]*)"', block)
        dt = time_match.group(1) if time_match else ""
        
        if text:
            results.append({"time": dt, "text": text[:1000]})

    return results

def main():
    all_results = []
    method = "none"

    for url in URLS:
        print(f"🔍 Trying {url}...")
        html = try_fetch(url)
        if not html:
            continue

        if "tgme_widget_message" in html or "subscriber" in html.lower() or "nanoka" in html.lower():
            results = parse_messages(html)
            # 按时间降序
            results.sort(key=lambda x: x['time'], reverse=True)
            if results:
                method = url.replace("https://t.me/", "")
                all_results = results
                print(f"✅ Got {len(results)} messages from {method}")
                break
            else:
                print(f"⚠️ Got page but no messages parsed")
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

    print(f"📦 Total: {len(all_results)} messages saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
