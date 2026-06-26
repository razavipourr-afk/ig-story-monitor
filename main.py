import os
from playwright.sync_api import sync_playwright

IG_USERNAME = os.environ["IG_USERNAME"]
IG_PASSWORD = os.environ["IG_PASSWORD"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle", timeout=60000)

    page.fill('input[name="username"]', IG_USERNAME)
    page.fill('input[name="password"]', IG_PASSWORD)
    page.click('button[type="submit"]')

    page.wait_for_timeout(10000)

    print("PAGE TITLE:", page.title())
    print("PAGE URL:", page.url)
    print("PAGE LENGTH:", len(page.content()))

    content = page.content().lower()

    if "challenge" in page.url.lower() or "checkpoint" in page.url.lower():
        print("RESULT: LOGIN_CHALLENGE")
    elif "accounts/login" in page.url.lower():
        print("RESULT: LOGIN_FAILED")
    elif "instagram.com" in page.url.lower():
        print("RESULT: LOGIN_MAYBE_OK")
    else:
        print("RESULT: UNKNOWN")

    browser.close()
