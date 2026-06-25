import instaloader
import os
import requests

USERNAME = "instagram_username_to_monitor"
TARGET_PROFILE = "beautydealsbff"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

STATE_FILE = "state.txt"


def load_last_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return f.read().strip()


def save_state(value):
    with open(STATE_FILE, "w") as f:
        f.write(str(value))


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    })


def send_telegram_media(file_path, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(file_path, "rb") as f:
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": caption
        }, files={"photo": f})


def get_latest_story():
    loader = instaloader.Instaloader()

    # اگر نیاز شد لاگین اضافه میشه (برای public فعلاً لازم نیست)
    profile = instaloader.Profile.from_username(loader.context, TARGET_PROFILE)

    stories = loader.get_stories(userids=[profile.userid])

    latest = None

    for story in stories:
        for item in story.get_items():
            latest = item  # آخرین آیتم

    return latest


def extract_link(story_item):
    # Instaloader بعضی وقت‌ها لینک sticker را metadata می‌دهد
    try:
        if story_item._node and "story_cta_url" in story_item._node:
            return story_item._node["story_cta_url"]
    except:
        pass
    return None


def download_story(item):
    filename = f"{item.mediaid}.jpg"
    instaloader.Instaloader().download_pic(filename, item.url, item.date_utc)
    return filename


def main():
    last_id = load_last_state()

    story = get_latest_story()

    if not story:
        print("No story found")
        return

    current_id = str(story.mediaid)

    if last_id == current_id:
        print("No new story")
        return

    print("New story detected!")

    link = extract_link(story)

    caption = f"""📢 New Story: {TARGET_PROFILE}

🕒 {story.date_utc}

🔗 Link:
{link if link else 'No link found'}
"""

    # دانلود مدیا
    file_path = f"/tmp/{current_id}.jpg"
    story.download_pic(file_path, story.url)

    # ارسال به تلگرام
    send_telegram_media(file_path, caption)

    # ذخیره state
    save_state(current_id)


if __name__ == "__main__":
    main()
