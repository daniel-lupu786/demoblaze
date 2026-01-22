from playwright.sync_api import expect

from tests.pages.cart_page import CartPage
from tests.pages.home_page import HomePage
from tests.pages.products_page import ProductPage


class T002data:
    product_name = "Nokia lumia 1520"

def test_remove_item_from_cart(page, log):
    home = HomePage(page, log)
    product = ProductPage(page, log)
    cart = CartPage(page, log)

    home.open()
    home.open_product(T002data.product_name)
    product.add_to_cart_accept_alert()

    cart.navigate_to()
    expect(cart.rows).to_have_count(1)

    cart.delete_first_item()
    expect(cart.rows).to_have_count(0)
