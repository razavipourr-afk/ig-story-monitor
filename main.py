from playwright.sync_api import sync_playwright

URL = "https://www.instagram.com/beautydealsbff/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)

    print("PAGE TITLE:", page.title())
    print("PAGE URL:", page.url)
    print("PAGE LENGTH:", len(page.content()))

    if "beautydealsbff" in page.content():
        print("RESULT: PAGE_ACCESS_OK")
    else:
        print("RESULT: PAGE_ACCESS_FAILED")

    browser.close()
