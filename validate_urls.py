#!/usr/bin/env python3
import asyncio
import time
from pathlib import Path

from playwright.async_api import async_playwright

INPUT_FILE = "generated_codes.txt"
OUTPUT_FILE = "playwright_validation_results.txt"
MAX_URLS = 10  # Set None to scan all URLs
PAGE_TIMEOUT_MS = 15000  # 15 seconds per page
HEADLESS = False  # Show the browser so the user can watch
VIEW_PAUSE_MS = 10000  # Pause 10s between pages so user can see
# Prefer attaching to an existing Chrome window started with --remote-debugging-port=9222
USE_EXISTING_BROWSER = True
CDP_ENDPOINT = "http://localhost:9222"

# Text markers that indicate the promo dialog is shown
PROMO_MARKERS = [
    "Promo Unavailable",
    "don't meet the eligibility criteria",
    "dont meet the eligibility criteria",  # fallback without apostrophe
]


async def check_url_with_page(page, url: str):
    status_code = None
    promo_found = False
    message = ""

    try:
        response = await page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
        if response:
            status_code = response.status
        # Check if promo dialog/message exists
        # 1) Try visible dialog with the key text
        try:
            locator = page.get_by_text("Promo Unavailable")
            await locator.first.wait_for(state="visible", timeout=3000)
            promo_found = True
        except Exception:
            promo_found = False

        # 2) If not found, search full HTML for any marker substring
        if not promo_found:
            html = await page.content()
            lower_html = html.lower()
            promo_found = any(marker.lower() in lower_html for marker in PROMO_MARKERS)

        message = f"HTTP {status_code if status_code is not None else 'N/A'} | promo_found={promo_found}"
    except Exception as e:
        promo_found = False
        message = f"Error: {str(e)}"

    return promo_found, message


async def main():
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    with input_path.open("r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    urls = urls[:MAX_URLS]
    print(f"Validating {len(urls)} URLs with Playwright...")

    results = []
    start = time.time()

    async with async_playwright() as p:
        browser = None
        context = None
        page = None

        # Try to attach to an existing Chrome instance via CDP
        if USE_EXISTING_BROWSER:
            try:
                browser = await p.chromium.connect_over_cdp(CDP_ENDPOINT)
                # Use the first available context/page in the existing window
                context = browser.contexts[0] if browser.contexts else None
                if context is not None and context.pages:
                    page = context.pages[0]
                elif context is not None:
                    page = await context.new_page()
                # If for some reason no context, fall back to launch
            except Exception:
                browser = None

        # Fallback: launch a new visible browser window
        if browser is None:
            browser = await p.chromium.launch(headless=HEADLESS, args=["--start-maximized"])
            context = await browser.new_context(
                viewport=None,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            )
            page = await context.new_page()

        # Let the user perform login before validation begins
        try:
            print("Opening login page... Please complete login in the browser window.")
            await page.goto("https://chatgpt.com", timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
        except Exception:
            # Ignore if navigation fails; the user might already be on a valid page
            pass

        # Wait for user's confirmation to proceed
        try:
            proceed = input("התחבר/י בדפדפן ואז לחץ/י Enter כדי להתחיל בבדיקה...")
        except Exception:
            proceed = ""

        for idx, url in enumerate(urls, start=1):
            print(f"[{idx}/{len(urls)}] {url[:70]}...", end=" ")
            found, msg = await check_url_with_page(page, url)
            results.append((url, found, msg))
            print("Found" if found else "Not Found", "-", msg)
            # Give the user time to see the page
            await page.wait_for_timeout(VIEW_PAUSE_MS)

        # Close only if we launched the browser ourselves; if attached, keep user's window
        if context and browser and browser.is_connected():
            if not USE_EXISTING_BROWSER or not browser.contexts or context not in browser.contexts:
                await context.close()
        if browser and browser.is_connected() and (not USE_EXISTING_BROWSER):
            await browser.close()

    duration = time.time() - start
    print(f"Done in {duration:.1f}s")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("Playwright URL Validation Results\n")
        out.write("=" * 60 + "\n\n")
        for url, found, msg in results:
            status = "PROMO_FOUND" if found else "PROMO_NOT_FOUND"
            out.write(f"{status}: {url}\n")
            out.write(f"Message: {msg}\n")
            out.write("-" * 60 + "\n")

    found_count = sum(1 for _, found, _ in results if found)
    print(f"Summary: promo found on {found_count}/{len(results)} pages. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
