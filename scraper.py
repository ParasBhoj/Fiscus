import asyncio
import urllib.parse
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

import config

def clean_html_to_text(html_content: str) -> str:
    """
    Cleans raw HTML and extracts the main text body using Trafilatura, 
    an advanced algorithm that automatically strips out navigation, footers, and ads.
    """
    import trafilatura
    text = trafilatura.extract(html_content)
    if not text:
        # Ultimate fallback: extract from body text using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        body = soup.find("body")
        if body:
            return body.get_text(separator="\n", strip=True)
        return soup.get_text(separator="\n", strip=True)
    return text


async def scrape_single_url(url: str, progress_callback=None) -> str:
    """
    Crawls a specific press release URL and extracts its full text content, bypassing anti-bot measures.
    """
    async with async_playwright() as p:
        if progress_callback:
            progress_callback(f"Launching stealth browser for {url}...")
            
        # Launch Chromium with anti-bot bypass parameters
        browser = await p.chromium.launch(
            headless=config.HEADLESS_MODE,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security"
            ]
        )
        
        # Create browser context with a modern, realistic user-agent
        context = await browser.new_context(
            user_agent=config.USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            }
        )
        
        page = await context.new_page()
        
        # Inject standard JS bypass for webdriver detection
        await page.add_init_script("delete navigator.__proto__.webdriver")
        
        if progress_callback:
            progress_callback(f"Navigating to: {url}")
            
        try:
            # Navigate to the detail page
            response = await page.goto(url, timeout=config.PLAYWRIGHT_TIMEOUT_MS, wait_until="domcontentloaded")
            if response and response.status >= 400:
                if progress_callback:
                    progress_callback(f"[bold red]Failed to load page, status code: {response.status}[/bold red]")
                await browser.close()
                return ""
                
            # Wait a short delay to ensure any dynamic rendering table displays
            await page.wait_for_timeout(1500)
            
            detail_html = await page.content()
            clean_text = clean_html_to_text(detail_html)
            
            await browser.close()
            return clean_text
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"[bold red]Error scraping {url}: {e}[/bold red]")
            await browser.close()
            return ""

if __name__ == "__main__":
    # Test execution
    async def test():
        print("Testing scraper module...")
        url = "https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=62972"
        text = await scrape_single_url(url, progress_callback=print)
        print("CONTENT LENGTH:", len(text))
        print(text[:500])
            
    asyncio.run(test())
