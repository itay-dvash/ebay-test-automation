# eBay E2E Automation Assignment

This is an automated testing project for eBay, developed as an assignment submission. It uses **Python**, **Playwright**, and **Pytest** to simulate a user searching for items, adding them to the shopping cart, and validating the final price. The project is built using the Page Object Model (POM) design pattern to keep the code organized and readable.

## 📁 Project Structure

```text
├── data/                       # Test data and configuration files
├── docs/                       # The answers for section (5) of the assignment
├── logs/                       # Execution logs
│   └── scrrenshots/            # Product screenshots
├── reports/                    # Test run reports (e.g., Allure results)
├── src/
│   ├── pages/
│   │   ├── base_page.py        # Base class with shared Playwright interactions
│   │   ├── search_page.py      # Handles item search and pagination
│   │   ├── product_page.py     # Handles product variants and adding to cart
│   │   └── cart_page.py        # Handles cart validation
│   └── utils/
│       └── custom_logging.py   # Custom logger setup
├── tests/                      # Pytest test files
├── conftest.py                 # Pytest fixtures and browser configuration
├── pytest.ini                  # Pytest execution configuration file
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

## 📌 Assumptions & Limitations

* **Authentication Policy:** The automation executed as a **Guest user**. It does not perform user registration or authentication.

* **Currency Handling:** The script relies on the default currency displayed by eBay during the session (which is dynamically determined by eBay based on the execution environment's IP/location or default store settings). Price assertions adapt dynamically to the currency symbols and values scraped directly from the pages.

* **Anti-Bot Measures:** Since this project runs against a live production environment (eBay.com) without an API or staging sandbox, execution speeds and element interaction delays are optimized to mimic human behavior and reduce the risk of IP blocking or captcha challenges.

## 🧠 Classes Overview

### 1. `BasePage` <span style="font-size: 16px">&nbsp;**(** *src/pages/base_page.py* **)**</span>
The parent class for all page objects. It initializes the Playwright `Page` instance and provides common helper methods (like waiting for elements, getting text, etc.) to avoid code duplication.

### 2. `SearchPage` <span style="font-size: 16px">&nbsp;**(** *src/pages/search_page.py* **)**</span>
Handles searching for items and collecting their URLs based on constraints (like max price and quantity limit).
* **Attributes:**
  * `BASE_SEARCH_URL` - Base endpoint for eBay search
* **Key Selectors:**
  * `ERROR_INDICATION` - Target element to dynamically detect eBay error pages.
  * `RESULT_COUNT_SELECTOR` - Target locator for total search results count heading.
  * `ITEM_WRAPPER` - Main outer container for individual product cards.
  * `PRICE_SELECTOR` - Product price element
  * `LINK_SELECTOR` - Product link anchor within the card
* **Main Method:**
  * `search_items_by_name_under_price(query: str, max_price: float, limit: int = 5) -> list[str]`

    Queries the marketplace for items and compiles a list of valid product URLs

### 3. `ProductPage` <span style="font-size: 16px">&nbsp;**(** *src/pages/product_page.py* **)**</span>
Manages interactions on the individual product page, including handling dropdowns for item variants and taking screenshots.
* **Key Selectors:**
  * `ADD_TO_CART_BUTTON` - The primary button to add the selected product to the cart.
  * `VARIANT_CONTAINERS` - Elements representing different product variations (like size or color).
  * `DROPDOWN_BUTTON` - The selector for opening a selection menu.
  * `LISTBOX_OPTIONS` - List of available options within an open dropdown.
  * `INTERFERING_HEADER` - Element that might overlay or block the view during screenshot
  * `SCRRENSHOT_DIV` - The specific container area to capture for screenshot

* **Main Method:**
  * `add_items_to_cart(urls: list[str]) -> None`

    Iterates over the collected URLs, handles necessary variant selections, and adds each item to the cart.

### 4. `CartPage` <span style="font-size: 16px">&nbsp;**(** *src/pages/cart_page.py* **)**</span>
Handles validations inside the shopping cart to ensure the logic worked correctly.
* **Attributes:**
  * `CART_URL` - Direct endpoint for eBay cart.
* **Key Selectors:**
  * `SUBTOTAL_SELECTOR` - The element containing the total price calculation in the cart.
* **Main Method:**
  * `assert_cart_total_not_exceeds(budget_per_item: float, items_count: int) -> None`

    Calculates the expected maximum total and asserts that the actual cart subtotal does not exceed this amount.

## ⚙️ Prerequisites

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd ebay-automation-project
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright Browsers:**
   ```bash
   playwright install
   ```

## 🚀 How to Run the Tests

**Run the Tests**
   Execute E2E flow by Pytest from the root directory:
   ```bash
   pytest tests
   ```

**View the Report:**
   Launch the Allure dashboard to view the results:
   ```bash
  allure serve reports/allure-results
  ```
  ** **Note:** You must have Allure installed on your system ([installation guide](https://allurereport.org/docs/v2/install/))