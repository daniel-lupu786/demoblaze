import pytest

from tests.pages.home_page import HomePage
from tests.pages.products_page import ProductPage


@pytest.fixture
def add_product_to_cart(page,log):
    home = HomePage(page,log)
    product = ProductPage(page, log)
    home.open()
    home.open_product("Sony vaio i5")
    product.add_to_cart_accept_alert()