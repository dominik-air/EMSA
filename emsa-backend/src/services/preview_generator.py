import asyncio
from io import BytesIO
import aiohttp
from playwright.async_api import async_playwright
import re
from PIL import Image

async def fetch_youtube_thumbnail(url):
    video_id = extract_video_id(url)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail_url) as response:
            return await response.read()  # Returns image as bytes

async def fetch_tiktok_logo():
    with open(r"emsa-backend\assets\thumbnails\tiktok_logo.png", "rb") as f:
        return f.read() # Returns image as bytes

async def fetch_website_screenshot(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await close_popups(page)
        screenshot = await page.screenshot()
        await browser.close()
        return screenshot  # Returns screenshot as bytes

async def link_preview_generator(link):
    if "youtube.com" in link:
        return await fetch_youtube_thumbnail(link)
    elif "tiktok.com" in link:
        return await fetch_tiktok_logo()
    else:
        return await fetch_website_screenshot(link)

def extract_video_id(url):
    """
    Extracts the YouTube video ID from a URL.
    """
    # Regular expression for various YouTube URL formats
    regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    
    match = re.search(regex, url)
    if match:
        return match.group(1)
    else:
        return None  # Or handle this case as needed
    
async def close_popups(page):
    # List of common selectors used in popups
    popup_selectors = [
        "button[aria-label='Close']", 
        "button[class*='close']", 
        "div[class*='popup'] button", 
        "[id*='popup'] button",
        "button:has-text('No thanks')",
        "button:has-text('Dismiss')"
        # Add more selectors as needed
    ]

    for selector in popup_selectors:
        # Check if the element exists and is visible
        if await page.is_visible(selector):
            # Click on the popup close button
            await page.click(selector)
            # Add a small delay if needed to wait for the popup to close
            await asyncio.sleep(0.5)
