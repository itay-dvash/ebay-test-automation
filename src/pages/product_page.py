import random
from src.pages.base_page import BasePage
from playwright.async_api import Locator


class ProductPage(BasePage):
    """
    Handles interactions on individual eBay product pages, including variant selection
    and adding items to the shopping cart.
    """

    # Selector for Add to Cart Button
    ADD_TO_CART_BUTTON: str = "#atcBtn_btn_1, #isCartBtn_btn"

    # Selectors for Dropdowns/Variant
    VARIANT_CONTAINERS: str = "div.vim.x-sku"
    DROPDOWN_BUTTON: str = "button.listbox-button__control"
    LISTBOX_OPTIONS: str = "div[role='listbox'] [role='option']"

    # Selectors for Capture Adjustments
    INTERFERING_HEADER: str = "#gh"
    SCRRENSHOT_DIV: str = "#CenterPanel"

    async def add_items_to_cart(self, urls: list[str]) -> None:
        """
        Iterates through product URLs, selects random variants if required,
        adds each to the cart, and records products with screenshots.

        Parameters
        ----------
        urls : list[str]
            List of collected product URLs
        """

        self.logger.info("STEP 2: Adding items to cart...")

        # Process each product URL sequentially to manage cart additions
        for item_index, url in enumerate(urls):
            # Navigate to the product page
            await self.page.goto(url)

            # Capture screenshot for audit trailing
            item_id = url.split("/")[-1]
            screenshot_path = (
                self.screenshot_dir / f"item_{item_index + 1:02d}_{item_id}.png"
            )
            await self.page.locator(self.INTERFERING_HEADER).evaluate(
                "el => el.style.display = 'none'")
            await self.page.locator(self.SCRRENSHOT_DIV).screenshot(path=screenshot_path)

            # Get the total count of dropdown containers
            container_count = await self.page.locator(self.VARIANT_CONTAINERS).count()

            # Handle dropdowns
            for i in range(container_count):
                # Perform dynamic relocation of the container to avoid stale elements
                container = self.page.locator(self.VARIANT_CONTAINERS).nth(i)

                # Click the dropdown button
                dropdown_button = container.locator(self.DROPDOWN_BUTTON)
                await self.click(dropdown_button)

                # Collect only the valid options from the dropdown
                listbox = container.locator(self.LISTBOX_OPTIONS)
                await listbox.first.wait_for(state="visible", timeout=3000)

                options = await listbox.all()
                valid_options: list[Locator] = []

                for opt in options:
                    if not await opt.is_visible():
                        continue

                    opt_text = await self.get_text(opt)

                    is_concrete = all(
                        phrase not in opt_text for phrase in ["Select", "Out of stock"]
                    )
                    is_disabled = (await opt.get_attribute("aria-disabled")) == "true"

                    if is_concrete and not is_disabled:
                        valid_options.append(opt)

                # Select a random option
                random_choice = random.choice(valid_options)

                await self.click(random_choice)
                await self.page.keyboard.press("Escape")
                await self.page.wait_for_timeout(500)

            # Add to cart
            await self.click(self.ADD_TO_CART_BUTTON)
            await self.page.wait_for_timeout(3000)
            self.logger.info(
                f"Added item [{item_index + 1:02d}/{len(urls):02d}] to cart. " \
                f"Screenshot saved to {screenshot_path}"
            )
