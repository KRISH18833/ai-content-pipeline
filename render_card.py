from pathlib import Path
from playwright.sync_api import sync_playwright

html = Path("linkedin_card.html").resolve().as_uri()
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1200, "height": 627}, device_scale_factor=2)
    page.goto(html)
    page.locator(".card").screenshot(path="linkedin_card.png")
    b.close()
print("Saved linkedin_card.png")
