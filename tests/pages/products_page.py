from playwright.sync_api import Page

class ProductPage:
    def __init__(self, page: Page, log):
        self.page = page
        self.name = page.locator(".name")
        self.add_to_cart = page.get_by_role("link", name="Add to cart")
        self.log = log

    def add_to_cart_accept_alert(self):
        self.add_to_cart.click()
        dialog = self.page.wait_for_event("dialog")
        dialog.accept()
