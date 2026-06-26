import os
from playwright.sync_api import sync_playwright

IG_USERNAME = os.environ["IG_USERNAME"]
IG_PASSWORD = os.environ["IG_PASSWORD"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    page.get_by_label("Mobile number, username or email").fill(IG_USERNAME)
    page.get_by_label("Password").fill(IG_PASSWORD)
    page.get_by_text("Log in", exact=True).click()

    page.wait_for_timeout(15000)

    print("PAGE TITLE:", page.title())
    print("PAGE URL:", page.url)
    print("PAGE LENGTH:", len(page.content()))

    body_text = page.locator("body").inner_text(timeout=5000)
    print("BODY TEXT START:")
    print(body_text[:1000])

    if "challenge" in page.url.lower() or "checkpoint" in page.url.lower():
        print("RESULT: LOGIN_CHALLENGE")
    elif "incorrect" in body_text.lower() or "password" in body_text.lower() and "incorrect" in body_text.lower():
        print("RESULT: LOGIN_FAILED")
    elif "accounts/login" in page.url.lower():
        print("RESULT: STILL_ON_LOGIN")
    else:
        print("RESULT: LOGIN_MAYBE_OK")

    browser.close()
