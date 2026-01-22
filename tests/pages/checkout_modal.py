from playwright.sync_api import Page

class CheckoutModal:
    def __init__(self, page: Page, log):
        self.page = page
        self.order_modal= page.locator("#orderModal")
        self.name = page.locator("#name")
        self.country = page.locator("#country")
        self.city = page.locator("#city")
        self.card = page.locator("#card")
        self.month = page.locator("#month")
        self.year = page.locator("#year")
        self.purchase = page.get_by_role("button", name="Purchase")
        self.confirm_title = page.locator(".sweet-alert h2")
        self.log = log

    def fill(self, data: dict):
        self.log.info("Filling: %s", data)
        self.name.fill(data["name"])
        self.country.type(data["country"])
        self.city.type(data["city"])
        self.card.type(data["card"])
        self.month.type(data["month"])
        self.year.type(data["year"])


    def submit(self):
        self.log.info("Submit: %s", self.name)
        self.purchase.click(no_wait_after=True)

    def submit_and_capture_alert(self) -> str | None:
        alert_text = {"value": None}

        def on_dialog(d):
            alert_text["value"] = d.message
            d.accept()

        self.page.once("dialog", on_dialog)
        self.submit()
        self.page.wait_for_timeout(100)

        return alert_text["value"]
