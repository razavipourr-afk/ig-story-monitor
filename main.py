from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(10000)

    print("PAGE TITLE:", page.title())
    print("PAGE URL:", page.url)
    print("PAGE LENGTH:", len(page.content()))

    inputs = page.locator("input").count()
    buttons = page.locator("button").count()
    print("INPUT COUNT:", inputs)
    print("BUTTON COUNT:", buttons)

    print("BODY TEXT START:")
    print(page.locator("body").inner_text(timeout=5000)[:1000])

    browser.close()
