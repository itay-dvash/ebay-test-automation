import pytest_asyncio
from playwright.async_api import async_playwright


@pytest_asyncio.fixture(scope="function")
async def async_page():
    """
    Custom async fixture to avoid event loop conflicts with the default sync playwright plugin.
    Provides a clean maximized browser context for each test and ensures teardown.
    """
    async with async_playwright() as p:
        # Headless=False allows you to watch the browser execution during debugging
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        yield page

        await context.close()
        await browser.close()
