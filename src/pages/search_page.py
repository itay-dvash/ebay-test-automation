from urllib.parse import urlencode
from src.pages.base_page import BasePage


class SearchPage(BasePage):
    """
    Handles product searching, price filtering, and pagination on eBay.
    """

    # eBay's Search URL
    BASE_SEARCH_URL: str = "https://www.ebay.com/sch/i.html"

    # Page Selectors
    ERROR_INDICATION: str = "#error-info"
    RESULT_COUNT_SELECTOR: str = "h1.srp-controls__count-heading>:first-of-type"

    # Item Selectors
    ITEM_WRAPPER: str = "#srp-river-results div.su-card-container"
    PRICE_SELECTOR: str = ".s-card__price"
    LINK_SELECTOR: str = "a.s-card__link"

    async def search_items_by_name_under_price(
        self, query: str, max_price: float, limit: int = 5
    ) -> list[str]:
        """
        Returns a list of item URLs extracted based on the search query,
        the max price filter, and item limit constraints.

        Parameters
        ----------
            query : str
                The search query string used to look up products.
            max_price : float
                Maximum threshold for item pricing.
            limit : int
                Maximum number of specific unique item URLs to collect.

        Returns
        -------
        list[str]
        """

        self.logger.info("STEP 1: Collecting item URLs according to filter details...")

        page_num: int = 1
        collected_urls: list[str] = []

        # Count the number of consecutive errors in an item parsing
        consecutive_errors: int = 0

        while len(collected_urls) < limit:
            # Build encoded search URL and navigates to the results page
            query_params = {
                "_nkw": query,      # Search Text (e.g. 'shoes')
                "_udhi": max_price, # Ceiling Price
                "_pgn": page_num,   # Page Number
                "LH_FS": 1,         # Free Shipping
                "LH_BIN": 1,        # Buy It Now - filter 'Auction'
              # "_fcid": 100        # Feed Country ID of Israel
            }
            search_url = f"{self.BASE_SEARCH_URL}?{urlencode(query_params)}"
            await self.page.goto(search_url, wait_until="domcontentloaded")

            # Stop execution if eBay error page is detected
            error_locator = self.page.locator(self.ERROR_INDICATION)

            if await error_locator.count() > 0:
                self.logger.error("Error page detected")
                break

            # Stop search when no matching results are found (Last page or zero results)
            result_count_text = await self.get_text(self.page.locator(self.RESULT_COUNT_SELECTOR))

            if result_count_text == "0":
                self.logger.info(
                    f"No items found on page {page_num} (or end of results). Stopping search."
                )
                break

            # Locate all product containers and get the total count
            items_locator = self.page.locator(self.ITEM_WRAPPER)
            items_count = await items_locator.count()

            self.logger.info(f"Found {items_count} product cards on page {page_num}.")

            # Iterate over each item by index
            for i in range(items_count):
                try:
                    # Access the specific item to retrieve its URL
                    item = items_locator.nth(i)
                    item_url = await item.locator(
                        self.LINK_SELECTOR).first.get_attribute("href")

                    # Validation check
                    if (item_url := item_url.split("?")[0]) in collected_urls:
                            continue

                    # Append the item URL to the collection
                    collected_urls.append(item_url)
                    consecutive_errors = 0

                    # Extract the item price from the UI for loggging
                    try:
                        price_locator = item.locator(self.PRICE_SELECTOR).first
                        price_text = await self.get_text(price_locator)
                    except Exception:
                        price_text = ""

                    self.logger.info(
                        f"Collected URL [{len(collected_urls):02d}/{limit:02d}]: {item_url}" + 
                        (f" (Price = {price_text})" if price_text else "")
                    )

                    # Stop collection when reaching the limit
                    if len(collected_urls) == limit:
                        break

                except Exception as e:
                    consecutive_errors += 1

                    if consecutive_errors < 3:
                        self.logger.warning(f"Could not parse item: {str(e)}")
                        continue
                    else:
                        self.logger.error(f"Too many parsing item errors. Stopping search.")
                        break

            else:
                # Handle pagination
                page_num += 1
                continue

            break

        return collected_urls
