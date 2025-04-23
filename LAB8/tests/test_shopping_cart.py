import pytest
from src.shopping_cart import Product, ShoppingCart


@pytest.fixture
def sample_products():
    return [
        Product(1, "Laptop", 2500.00),
        Product(2, "Mouse", 50.00),
        Product(3, "Keyboard", 150.00),
        Product(4, "Monitor", 800.00)
    ]


@pytest.fixture
def empty_cart():
    return ShoppingCart()


@pytest.fixture
def cart_with_products(empty_cart, sample_products):
    cart = empty_cart
    cart.add_product(sample_products[0])  # Add 1 laptop
    cart.add_product(sample_products[1], 2)  # Add 2 mice
    return cart


def test_add_single_product(empty_cart, sample_products):
    empty_cart.add_product(sample_products[0])

    assert len(empty_cart.products) == 1
    assert empty_cart.products[1]["product"] == sample_products[0]
    assert empty_cart.products[1]["quantity"] == 1


def test_add_multiple_quantity(empty_cart, sample_products):
    empty_cart.add_product(sample_products[1], 3)

    assert len(empty_cart.products) == 1
    assert empty_cart.products[2]["product"] == sample_products[1]
    assert empty_cart.products[2]["quantity"] == 3


def test_add_same_product_multiple_times(empty_cart, sample_products):
    empty_cart.add_product(sample_products[0], 2)
    empty_cart.add_product(sample_products[0], 3)

    assert len(empty_cart.products) == 1
    assert empty_cart.products[1]["quantity"] == 5


def test_add_product_invalid_quantity(empty_cart, sample_products):
    with pytest.raises(ValueError, match="Quantity must be positive"):
        empty_cart.add_product(sample_products[0], 0)

    with pytest.raises(ValueError, match="Quantity must be positive"):
        empty_cart.add_product(sample_products[0], -2)


def test_remove_product_complete(cart_with_products):
    cart_with_products.remove_product(1)  # Remove the laptop

    assert 1 not in cart_with_products.products
    assert len(cart_with_products.products) == 1
    assert 2 in cart_with_products.products  # Mouse should still be there


def test_remove_product_partial(cart_with_products):
    cart_with_products.remove_product(2, 1)  # Remove 1 of 2 mice

    assert 2 in cart_with_products.products
    assert cart_with_products.products[2]["quantity"] == 1


def test_remove_product_all_quantity(cart_with_products):
    cart_with_products.remove_product(2, 2)  # Remove both mice

    assert 2 not in cart_with_products.products
    assert len(cart_with_products.products) == 1


def test_remove_product_not_in_cart(cart_with_products):
    with pytest.raises(ValueError, match="Product not in cart"):
        cart_with_products.remove_product(99)


def test_remove_product_invalid_quantity(cart_with_products):
    with pytest.raises(ValueError, match="Quantity must be positive"):
        cart_with_products.remove_product(1, 0)

    with pytest.raises(ValueError, match="Quantity must be positive"):
        cart_with_products.remove_product(1, -1)


def test_get_total_price(cart_with_products, sample_products):
    expected_total = sample_products[0].price + (sample_products[1].price * 2)

    assert cart_with_products.get_total_price() == expected_total


@pytest.mark.parametrize("products_to_add, expected_total", [
    ([(0, 1)], 2500.00),  # 1 laptop
    ([(1, 2), (2, 1)], 250.00),  # 2 mice + 1 keyboard
    ([(0, 1), (1, 1), (2, 1), (3, 1)], 3500.00)  # 1 of each product
])
def test_get_total_price_parametrized(empty_cart, sample_products,
                                      products_to_add, expected_total):
    for idx, qty in products_to_add:
        empty_cart.add_product(sample_products[idx], qty)

    assert empty_cart.get_total_price() == expected_total


def test_get_product_count(cart_with_products):
    assert cart_with_products.get_product_count() == 3

    cart_with_products.add_product(cart_with_products.products[1]["product"],
                                   3)
    assert cart_with_products.get_product_count() == 6