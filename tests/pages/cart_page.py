from playwright.sync_api import Page

import config


class CartPage:
    URL = config.base_url + "cart.html"

    def __init__(self, page: Page, log):
        self.page = page
        self.rows = page.locator("#tbodyid > tr")
        self.place_order = page.get_by_role("button", name="Place Order")
        self.cart_icon = page.locator("#cartur")
        self.log = log

    def open(self):
        self.log.info("Opening Cart via URL")
        self.page.goto(self.URL, wait_until="domcontentloaded")

    def navigate_to(self):
        self.log.info("Pressing cart icon")
        self.cart_icon.click()


    def delete_first_item(self):
        self.rows.first.get_by_role("link", name="Delete").click()

    def open_checkout(self):
        self.place_order.click()
