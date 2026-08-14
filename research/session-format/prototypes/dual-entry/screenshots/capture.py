from playwright.sync_api import sync_playwright
import sys

BASE = "http://127.0.0.1:4321"
OUT_DIR = "screenshots"

PAGES = [
    ("index", "/", "01-home.png"),
    ("by-method", "/by-method", "02-by-method.png"),
    ("by-project", "/by-project", "03-by-project.png"),
    ("unit-detail", "/unit/unit-cyber-game-m9-001", "04-unit-detail.png"),
    ("unit-with-diff", "/unit/unit-cyber-game-m9-002", "05-unit-diff.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1200})

    for name, path, filename in PAGES:
        url = f"{BASE}{path}"
        print(f"Capturing {name}: {url}")
        page.goto(url)
        page.wait_for_load_state("networkidle")
        # Expand the first diff details on unit pages and scroll to the three-column layout
        if name.startswith("unit"):
            page.locator("details.diff-file").first.evaluate("el => el.open = true")
            page.wait_for_timeout(200)
            page.locator(".detail-columns").scroll_into_view_if_needed()
            page.wait_for_timeout(200)
            page.screenshot(path=f"{OUT_DIR}/{filename}")
        else:
            page.screenshot(path=f"{OUT_DIR}/{filename}", full_page=True)
        print(f"  -> {OUT_DIR}/{filename}")

    browser.close()

print("Done.")
