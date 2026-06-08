from re import search
from src.pages.base_page import BasePage


class CartPage(BasePage):
    """
    Handles verification of the shopping cart total against a dynamic budget threshold.
    """

    # eBay's Cart URL
    CART_URL: str = "https://cart.ebay.com"

    # Selectors for eBay's Cart Elements
    SUBTOTAL_SELECTOR: str = "div[data-test-id='SUBTOTAL']"

    async def assert_cart_total_not_exceeds(
        self, budget_per_item: float, items_count: int
    ) -> None:
        """
        Navigates to the cart, handles potential anti-bot captchas,
        calculates the maximum budget ceiling, and asserts the total.

        Parameters
        ----------
            budget_per_item : float
                The maximum price allowed for a single product.
            items_count : int
                The total number of items in the shopping cart.
        """

        self.logger.info("STEP 3 (1/2): Retrieving the shopping cart total...")

        # Open the shopping cart page
        await self.page.goto(self.CART_URL)

        # Anti-Bot Check: Pause to let the user solve it manually
        if "captcha" in self.page.url:
            chaptcha_alert = (
                "Action Required: Please solve the CAPTCHA manually to continue."
            )
            self.page.on("dialog", lambda _: self.logger.critical(chaptcha_alert))
            await self.page.evaluate(f"alert('{chaptcha_alert}')")

            # Wait up to 60 seconds for the browser to redirect back to the cart page
            try:
                dynamic_url_pattern = self.CART_URL.replace("https://", "**/") + "**"
                await self.page.wait_for_url(dynamic_url_pattern, timeout=60000)
                self.logger.info(
                    "Captcha resolved successfully. Proceeding to subtotal validation."
                )

            except Exception as e:
                message = "Captcha challenge was not resolved within 60 seconds."
                self.logger.error(message)
                raise TimeoutError(message) from e

        # Ensure the subtotal element is fully rendered before extracting data
        await self.page.locator(self.SUBTOTAL_SELECTOR).wait_for(
            state="visible", timeout=15000
        )

        # Extract and parse the raw total numeric value from the UI
        try:
            total_text = await self.get_text(self.SUBTOTAL_SELECTOR)
            total = float(search(r"\d+\.\d+|\d+", total_text.replace(",", "")).group())

        except Exception as e:
            message = f"Failed to parse cart total from screen: {e}"
            self.logger.error(message)
            raise RuntimeError(message) from e

        # Calculate the maximum allowed threshold (the ceiling)
        max_allowed_budget = budget_per_item * items_count

        # Capture screenshot of the cart page before making the assertion
        screenshot_path = self.screenshot_dir / "cart_summary.png"
        await self.page.screenshot(path=screenshot_path)
        self.logger.info(f"Cart screenshot saved to {screenshot_path}")

        # Perform the final structural assertion
        self.logger.info("STEP 3 (2/2): Asserting budget compliance...")

        try:
            assert total <= max_allowed_budget
            self.logger.info(
                f"Assertion Passed! Cart total ({total}) is within the budget limit ({max_allowed_budget})."
            )
        except AssertionError:
            self.logger.error(
                f"Assertion Failed: Cart total ({total}) exceeds the calculated budget cap ({max_allowed_budget})"
            )
            raise
