import json
import os.path

from playwright.sync_api import expect

from tests.pages.cart_page import CartPage
from tests.pages.checkout_modal import CheckoutModal
from tests.pages.home_page import HomePage
from tests.pages.products_page import ProductPage


class T003Data:
    product_name = "Sony vaio i5"
    file_path = os.path.realpath("utils/data/checkout.json")
    with open(file_path) as file:
        json = json.load(file)
    success_text = "Thank you for your purchase!"
    alert_text = "Please fill out"


def test_checkout_valid(page, log):
    home = HomePage(page, log)
    product = ProductPage(page, log)
    cart = CartPage(page, log)
    modal = CheckoutModal(page, log)

    home.open()
    home.open_product(T003Data.product_name)
    product.add_to_cart_accept_alert()

    cart.open()
    expect(cart.rows).to_have_count(1)
    cart.open_checkout()

    modal.fill(T003Data.json["valid"])

    modal.submit()
    expect(modal.confirm_title).to_have_text(T003Data.success_text)

def test_checkout_invalid_missing_required_fields(page, log):
    home = HomePage(page, log)
    product = ProductPage(page, log)
    cart = CartPage(page, log)
    modal = CheckoutModal(page, log)

    home.open()
    home.open_product(T003Data.product_name)
    product.add_to_cart_accept_alert()

    cart.open()
    cart.open_checkout()
    expect(modal.order_modal).to_be_visible()

    modal.fill(T003Data.json["invalid"])

    alert_message = modal.submit_and_capture_alert()

    print(alert_message)
    assert T003Data.alert_text in alert_message
