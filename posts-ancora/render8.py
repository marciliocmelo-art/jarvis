import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width":1080,"height":1350})
        await page.goto(f"file:///home/claude/jarvis/posts-ancora/post8.html")
        await page.wait_for_timeout(300)
        await page.screenshot(path="/home/claude/jarvis/posts-ancora/post8-final.png")
        await browser.close()

asyncio.run(main())
