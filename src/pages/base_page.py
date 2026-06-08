from os import getpid
from time import strftime
from pathlib import Path
from playwright.async_api import Page, Locator
from src.utils import global_logger


class BasePage:
    """
    Base class for all page objects, providing common browser interactions.

    All Page Objects should inherit from this class to ensure centralized
    timeout management, safe locators handling, and robust utilities.
    """

    _screenshot_dir: Path = (
        Path("logs/screenshots") /
        f"{strftime('%Y%m%d_%H%M%S')}_{getpid():05d}"
    )

    def __init__(self, page: Page) -> None:
        """Initializes the base page and ensures execution artifact directories exist."""
        self.page = page
        self.logger = global_logger
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)

    @property
    def screenshot_dir(self) -> Path:
        "Returns the configured root directory for page screenshots."
        return BasePage._screenshot_dir

    def _get_locator(self, target: str | Locator) -> Locator:
        """
        Helper method to resolve unified target input into a Playwright Locator.
        `.first` guards against strict-mode violations if multiple elements match).
        """
        if isinstance(target, str):
            return self.page.locator(target).first
        return target

    async def click(self, target: str | Locator, timeout: float = 5000) -> None:
        """
        Clicks an element, automatically waiting for it to become actionable.

        Parameters
        ----------
            target : str | Locator
                CSS Selector string or an existing Playwright Locator object.
            timeout : float
                Maximum time in milliseconds to wait for the action.
        """
        locator = self._get_locator(target)
        await locator.click(timeout=timeout, delay=100)

    async def get_text(self, target: str | Locator, timeout: float = 5000) -> str:
        """
        Retrieves the inner text of an element, or an empty string if none.

        Parameters
        ----------
            target : str | Locator
                CSS Selector string or an existing Playwright Locator object.
            timeout : float
                Maximum time in milliseconds to wait for the text retrieval.

        Returns
        -------
        str
        """
        locator = self._get_locator(target)
        text = await locator.inner_text(timeout=timeout)
        return text if text else ""
