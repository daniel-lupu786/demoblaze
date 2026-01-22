from playwright.sync_api import expect

from tests.pages.cart_page import CartPage
from tests.pages.home_page import HomePage
from tests.pages.products_page import ProductPage


class T001Data:
    product_name = "Samsung galaxy s6"


def test_add_product_to_cart(page, log):
    home = HomePage(page, log)
    product = ProductPage(page, log)
    cart = CartPage(page, log)

    home.open()

    home.open_product(T001Data.product_name)
    expect(product.name).to_have_text(T001Data.product_name)
    product.add_to_cart_accept_alert()

    # cart.open()
    cart.navigate_to()
    expect(cart.rows).to_have_count(1)
