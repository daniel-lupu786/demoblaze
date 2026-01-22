from playwright.sync_api import Page

import config


class HomePage:
    URL = config.base_url

    def __init__(self, page: Page, log):
        self.page = page
        self.grid = page.locator("#tbodyid")
        self.log = log

    def open(self):
        self.log.info("Open home: %s", self.URL)
        self.page.goto(self.URL, wait_until="domcontentloaded")
        self.grid.wait_for(timeout=2000)

    def open_product(self, name: str):
        self.log.info("Open product: %s", name)
        self.grid.get_by_role("link", name=name).click()
