import asyncio
import re

import aiohttp
from playwright.async_api import Page, async_playwright

from src.services.cloud_storage import CloudStorage, FailedToUploadImageException


async def fetch_youtube_thumbnail(url: str) -> bytes:
    video_id = extract_video_id(url)
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail_url) as response:
            return await response.read()


async def fetch_tiktok_logo() -> str:
    return "https://storage.googleapis.com/emsa-content/thumbnails/tiktok_logo"


async def fetch_website_screenshot(url: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await close_popups(page)
        screenshot = await page.screenshot()
        await browser.close()
        return screenshot


async def link_preview_generator(url: str) -> bytes | str:
    if "youtube.com" in url:
        return await fetch_youtube_thumbnail(url)
    elif "tiktok.com" in url:
        return await fetch_tiktok_logo()
    else:
        return await fetch_website_screenshot(url)


async def preview_link_upload(data: bytes, media_id: int) -> str:
    cloud_storage = CloudStorage()
    try:
        key = await cloud_storage.upload_image(str(media_id), data, "thumbnails")
    except FailedToUploadImageException:
        key = "preview_link_error"
    return key


def extract_video_id(url: str) -> None | str:
    """
    Extracts the YouTube video ID from a URL.
    """
    # Regular expression for various YouTube URL formats
    regex = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"

    match = re.search(regex, url)
    if match:
        return match.group(1)
    else:
        return None


async def close_popups(page: Page) -> None:
    # List of common selectors used in popups
    popup_selectors = [
        "button[aria-label='Close']",
        "button[class*='close']",
        "div[class*='popup'] button",
        "[id*='popup'] button",
        "button:has-text('No thanks')",
        "button:has-text('Dismiss')",
        # Add more selectors as needed
    ]

    for selector in popup_selectors:
        # Check if the element exists and is visible
        if await page.is_visible(selector):
            # Click on the popup close button
            await page.click(selector)
            # Add a small delay if needed to wait for the popup to close
            await asyncio.sleep(0.5)
