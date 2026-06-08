import json
from pathlib import Path
from typing import Any

import pytest
import allure
from playwright.async_api import Page
from src.pages import SearchPage, ProductPage, CartPage


def load_test_data() -> dict[str, Any]:
    """
    Loads test configuration and boundaries from an external JSON file.
    """
    data_path = Path("data/test_data.json")
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)


@allure.feature("eBay Shopping")
@allure.story("Search, Add To Cart And Validate Budget")
@pytest.mark.asyncio
async def test_ebay_e2e_budget_flow(async_page: Page) -> None:
    """
    E2E test scenario: Search items, add filtered items to cart, 
    and assert the subtotal does not exceed the budget threshold.
    """

    # Load Data-Driven values
    test_data = load_test_data()
    query: str = test_data["search_query"]
    max_price: float = test_data["max_price"]
    limit: int = test_data["item_limit"]

    # Set dynamic parameters for better report analysis
    allure.dynamic.parameter("Search Query", query)
    allure.dynamic.parameter("Max Price", max_price)
    allure.dynamic.parameter("Item Limit", limit)

    # Initialize Page Objects using our dedicated async fixture
    search_page = SearchPage(async_page)
    product_page = ProductPage(async_page)
    cart_page = CartPage(async_page)

    # Step 1: Open eBay and search for items under price criteria
    try:
        with allure.step(f"Search '{query}' under {max_price}$"):
            urls = await search_page.search_items_by_name_under_price(
                query=query, 
                max_price=max_price, 
                limit=limit
            )
    except TimeoutError as e:
        pytest.fail(f"Test failed during Search processing: {str(e)}")

    # Step 2: Add collected item URLs to the shopping cart
    if urls:
        try:
            with allure.step(f"Add {len(urls)} products to cart"):
                await product_page.add_items_to_cart(urls)
        except TimeoutError as e:
            pytest.fail(f"Test failed during Product processing: {str(e)}")

        # Step 3: Assert the cart total does not exceed the calculated limit
        try:
            with allure.step("Validate cart total"):
                await cart_page.assert_cart_total_not_exceeds(
                    budget_per_item=max_price, 
                    items_count=len(urls)
                )
        except (TimeoutError, RuntimeError, AssertionError) as e:
            pytest.fail(f"Test failed during Cart processing: {str(e)}")

    else:
        pytest.skip(f"No items found matching the criteria: '{query}' under {max_price}")
