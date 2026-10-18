"""ينشر الأخبار الجديدة فقط على قناة Telegram (عنوان + مصدر + رابط)."""
import html
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEWS = ROOT / "data" / "news.json"
STATE = ROOT / "state" / "posted.json"
SITE = "https://leader-vi7-gif.github.io/leader-vi7-games/"
MAX_PER_RUN = 5
KEEP_POSTED = 1500

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
PLAT = {"pc": "🖥 PC", "console": "🎮 Console", "mobile": "📱 Mobile"}


def send(text: str) -> bool:
    data = urllib.parse.urlencode({
        "chat_id": CHAT,
        "text": text,
        "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return bool(json.load(r).get("ok"))


def build(item: dict) -> str:
    tags = " ".join(PLAT[p] for p in item.get("platforms", []) if p in PLAT)
    meta = f"📰 {html.escape(item['source'])}" + (f" · {tags}" if tags else "")
    return (f"🔥 <b>{html.escape(item['title'])}</b>\n\n{meta}\n"
            f"🔗 <a href=\"{html.escape(item['link'], quote=True)}\">اقرأ الخبر</a>\n\n"
            f"🌐 <a href=\"{SITE}\">LEADER_GAMES</a>")


def save(posted: list) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(posted[-KEEP_POSTED:], ensure_ascii=False, indent=0),
                     encoding="utf-8")


def main() -> int:
    if not TOKEN or not CHAT:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set; skipping.")
        return 0
    if not NEWS.exists():
        print("news.json missing; skipping.")
        return 0

    items = json.loads(NEWS.read_text(encoding="utf-8"))["items"]
    first_run = not STATE.exists()
    posted = [] if first_run else json.loads(STATE.read_text(encoding="utf-8"))
    seen = set(posted)

    new = [i for i in items if i["link"] not in seen]
    if first_run:
        save([i["link"] for i in reversed(items)])
        print(f"First run: seeded {len(items)} items without posting.")
        return 0

    to_post = list(reversed(new[:MAX_PER_RUN]))
    skipped = new[MAX_PER_RUN:]
    posted.extend(i["link"] for i in skipped)

    sent = 0
    for item in to_post:
        try:
            if send(build(item)):
                posted.append(item["link"])
                sent += 1
        except Exception as exc:  # noqa: BLE001
            print(f"Telegram error: {exc}", file=sys.stderr)
            break
    save(posted)
    print(f"Posted {sent} new items ({len(skipped)} skipped).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
