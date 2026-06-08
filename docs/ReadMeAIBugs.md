# Bug-Dealing Exercise (Sec. 5) - Code Review

<br>

## The Code

``` py
from playwright.sync_api import sync_playwright
from selenium import webdriver
import time

def test_search_functionality():
    browser = sync_playwright().start().chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")

    time.sleep(2)

    search_box = page.locator("#search")
    search_box.fill("playwright testing")

    page.locator(".button").click()

    time.sleep(3)

    results = page.locator(".result-item")

    browser.close()
```

<br>

## Implementation Problems & Offered Solutions


### (1) *Mixing Automation Frameworks*

The code imports both `Playwright` and `Selenium`.
Even though Selenium is not used, Mixing multiple automation frameworks in the same project creates confusion, increases maintenance costs, and introduces unnecessary dependencies.

### *<u>Solution</u>: Remove the unused import*

Leaves the code with only one automation framework:

```py
from playwright.sync_api import sync_playwright
```

---

### (2) *Lack of Context Manager*

The Playwright instance is started manually but never stopped.
This may cause resource leaks and leave browser processes running after test execution.

### *<u>Solution</u>: Add a* <span style="font-size: 16px">`with`</span> *block to the Playwright instance*

```py
with sync_playwright() as p:
    browser = p.start().chromium.launch()
    ...
```

---

### (3) *The* <span style="font-size: 16px">`time.sleep`</span> *Usage*

The use of `time.sleep` introduces fixed waits that do not reflect the actual state of the application. If the application responds faster, execution time is wasted. If the application responds slower, the test may fail even though the functionality is correct.

### *<u>Solution</u>: Replace Static Waits with Event-Driven Synchronization*

A better approach is to use Playwright's explicit waiting mechanisms that synchronize the test with the application's real state (**e.g.**, `Locator.wait_for`).

```py
page.locator("#search").wait_for(state="visible")
```
