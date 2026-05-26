import requests
import json
import re
import os
from datetime import datetime

CHANNEL = "nanoka_news"
OUTPUT_FILE = "result.json"
TG_PREVIEW_URL = f"https://t.me/s/{CHANNEL}"

def try_fetch(url, timeout=20):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def parse_tg_html(html):
    results = []
    msg_pattern = re.findall(
        r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>\s*<div class="tgme_widget_message_date"[^>]*>.*?<time[^>]*datetime="([^"]*)"',
        html, re.DOTALL | re.IGNORECASE
    )
    for text, dt in msg_pattern[:10]:
        text = re.sub(r'<[^>]+>', '', text)
        text = text.strip()
        if text:
            results.append({"time": dt, "text": text[:500]})
    return results

def main():
    all_results = []
    fetch_method = "none"

    print("🔍 Trying t.me/s preview...")
    html = try_fetch(TG_PREVIEW_URL)
    if html and ("tgme_widget_message" in html or "subscriber" in html.lower()):
        results = parse_tg_html(html)
        if results:
            fetch_method = "t.me/s"
            all_results = results
            print(f"✅ Got {len(results)} messages via t.me/s")
        else:
            print("⚠️ Got HTML but no messages found")
    else:
        print("⚠️ t.me/s not accessible")

    output = {
        "channel": CHANNEL,
        "updated": datetime.utcnow().isoformat() + "Z",
        "method": fetch_method,
        "count": len(all_results),
        "messages": all_results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n📦 Total: {len(all_results)} messages from {fetch_method}")

if __name__ == "__main__":
    main()