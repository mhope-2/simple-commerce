import pytest


@pytest.mark.parametrize("id, status_code, res_data", [
    ("product1", 200, {"code": "product1", "name": "Product 1", "price": 9.99}),
    ("productX", 404, {"detail": "Product not found"}),
])
def test_retrieve_product(client, id, status_code, res_data):
    res = client.get(f"/products/{id}")
    assert res.status_code == status_code
    assert res.json() == res_data
