\
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from instagrapi import Client
from config import TARGET_PROFILES, CHECK_ONLY_STORIES_WITH_LINK

STATE_FILE = Path("state.json")
MAX_SEEN_IDS = 500


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


IG_USERNAME = get_env("IG_USERNAME")
IG_PASSWORD = get_env("IG_PASSWORD")
TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = get_env("TELEGRAM_CHAT_ID")


def load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {"seen_story_ids": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"seen_story_ids": []}


def save_state(state: Dict[str, Any]) -> None:
    seen = state.get("seen_story_ids", [])
    state["seen_story_ids"] = seen[-MAX_SEEN_IDS:]
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def telegram_api(method: str, data: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    response = requests.post(url, data=data, files=files, timeout=60)
    if not response.ok:
        print(f"Telegram error {response.status_code}: {response.text}", file=sys.stderr)


def send_text(text: str) -> None:
    telegram_api("sendMessage", {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": False,
    })


def download_file(url: str, suffix: str) -> Path:
    response = requests.get(url, timeout=90)
    response.raise_for_status()
    f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.write(response.content)
    f.close()
    return Path(f.name)


def send_media(file_path: Path, is_video: bool, caption: str) -> None:
    method = "sendVideo" if is_video else "sendPhoto"
    field = "video" if is_video else "photo"
    with open(file_path, "rb") as f:
        telegram_api(method, {"chat_id": TELEGRAM_CHAT_ID, "caption": caption[:1024]}, files={field: f})


def extract_links_from_story(story: Any) -> List[str]:
    links = []

    # روش‌های احتمالی؛ ساختار اینستاگرام ممکن است تغییر کند.
    candidates = [
        getattr(story, "links", None),
        getattr(story, "story_link_stickers", None),
        getattr(story, "reel_mentions", None),
    ]

    for candidate in candidates:
        if not candidate:
            continue

        if isinstance(candidate, list):
            items = candidate
        else:
            items = [candidate]

        for item in items:
            for attr in ["webUri", "web_uri", "url", "link", "uri"]:
                value = getattr(item, attr, None)
                if value and isinstance(value, str) and value.startswith("http"):
                    links.append(value)

            if isinstance(item, dict):
                for key in ["webUri", "web_uri", "url", "link", "uri"]:
                    value = item.get(key)
                    if value and isinstance(value, str) and value.startswith("http"):
                        links.append(value)

    # fallback: جستجو داخل مدل دیکشنری‌شده
    try:
        dumped = story.model_dump() if hasattr(story, "model_dump") else story.dict()
        text = json.dumps(dumped, ensure_ascii=False)
        import re
        links.extend(re.findall(r"https?://[^\"'\\\s]+", text))
    except Exception:
        pass

    # حذف تکراری‌ها با حفظ ترتیب
    result = []
    for link in links:
        if link not in result:
            result.append(link)
    return result


def story_id(story: Any) -> str:
    return str(getattr(story, "pk", None) or getattr(story, "id", None))


def story_taken_at(story: Any) -> str:
    return str(getattr(story, "taken_at", "") or "")


def story_media_url(story: Any) -> tuple[str, bool]:
    video_url = getattr(story, "video_url", None)
    if video_url:
        return str(video_url), True

    thumbnail_url = getattr(story, "thumbnail_url", None)
    if thumbnail_url:
        return str(thumbnail_url), False

    raise RuntimeError("No media URL found for story")


def build_caption(username: str, story: Any, links: List[str]) -> str:
    lines = [
        f"📢 New Story: {username}",
        f"🕒 {story_taken_at(story)}",
    ]

    if links:
        lines.append("")
        lines.append("🔗 Link:")
        lines.extend(links[:5])

    return "\n".join(lines)


def main() -> None:
    state = load_state()
    seen = set(state.get("seen_story_ids", []))

    client = Client()
    client.login(IG_USERNAME, IG_PASSWORD)

    new_seen = list(state.get("seen_story_ids", []))
    sent_count = 0

    for username in TARGET_PROFILES:
        print(f"Checking {username}...")

        user_id = client.user_id_from_username(username)
        stories = client.user_stories(user_id)

        # قدیمی‌ترها اول ارسال شوند.
        stories = sorted(stories, key=lambda s: story_taken_at(s))

        for story in stories:
            sid = f"{username}:{story_id(story)}"
            if sid in seen:
                continue

            links = extract_links_from_story(story)

            if CHECK_ONLY_STORIES_WITH_LINK and not links:
                new_seen.append(sid)
                continue

            try:
                media_url, is_video = story_media_url(story)
                suffix = ".mp4" if is_video else ".jpg"
                file_path = download_file(media_url, suffix)
                caption = build_caption(username, story, links)
                send_media(file_path, is_video, caption)
                file_path.unlink(missing_ok=True)
                sent_count += 1
                print(f"Sent story {sid}")
            except Exception as e:
                print(f"Failed to send story {sid}: {e}", file=sys.stderr)
                send_text(f"⚠️ Failed to send story from {username}\nStory ID: {sid}\nError: {e}")

            new_seen.append(sid)

    state["seen_story_ids"] = new_seen[-MAX_SEEN_IDS:]
    save_state(state)
    print(f"Done. Sent {sent_count} new stories.")


if __name__ == "__main__":
    main()
