"""Scrape a website URL: extract content as markdown and take multiple screenshots."""

import asyncio
import os
import requests
from playwright.async_api import async_playwright
from config import FIRECRAWL_API_KEY, OUTPUT_DIR


def scrape_content(url: str) -> str:
    """Use Firecrawl API to extract clean markdown from a URL."""
    resp = requests.post(
        "https://api.firecrawl.dev/v2/scrape",
        headers={
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", {}).get("markdown", "")


async def take_screenshots(url: str) -> list[str]:
    """
    Capture multiple screenshots of the website at different scroll positions.
    Returns a list of file paths to the screenshots.
    """
    screenshots = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        # Give dynamic content time to render
        await page.wait_for_timeout(3000)

        # Get page height
        page_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = 900

        # Take screenshots at different scroll positions
        num_shots = min(5, max(2, page_height // viewport_height + 1))
        scroll_positions = [
            int(i * (page_height - viewport_height) / max(1, num_shots - 1))
            for i in range(num_shots)
        ]

        for idx, scroll_y in enumerate(scroll_positions):
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            await page.wait_for_timeout(500)

            filename = f"screenshot_{idx}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)
            await page.screenshot(path=filepath)
            screenshots.append(filepath)
            print(f"  Screenshot {idx}: scrollY={scroll_y} -> {filepath}")

        await browser.close()

    return screenshots


if __name__ == "__main__":
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    print(f"Scraping: {url}")

    content = scrape_content(url)
    print(f"Content length: {len(content)} chars")
    print(content[:500])

    screenshots = asyncio.run(take_screenshots(url))
    print(f"Screenshots: {screenshots}")
