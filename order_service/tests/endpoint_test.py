import pytest


@pytest.mark.parametrize(
    "req_data, status_code, res_data",
    [
        (
            {"user_id": "7c11e1ce2741", "product_code": "product1", "quantity": 2},
            200,
            {
                "user_id": "7c11e1ce2741",
                "product_code": "product1",
                "product_name": "Product 1",
                "customer_full_name": "John Doe",
                "quantity": 2,
                "total_amount": 19.98,
            },
        ),
        (
            {"user_id": "7c11e1ce2741", "product_code": "product3", "quantity": 2},
            500,
            {"detail": "Exception occurred"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_order(
    test_client, status_code, req_data, res_data, mock_fetch_user, mock_fetch_product, mock_publish_message
):
    res = test_client.post(f"/orders/", json=req_data)

    assert res.status_code == status_code
    if status_code == 200:
        assert res.json()["user_id"] == res_data["user_id"]
        assert res.json()["product_code"] == res_data["product_code"]
        assert res.json()["product_name"] == res_data["product_name"]
        assert res.json()["customer_full_name"] == res_data["customer_full_name"]
        assert res.json()["quantity"] == res_data["quantity"]
        assert res.json()["total_amount"] == res_data["total_amount"]
    else:
        assert res.json() == res_data

    # Ensure the publish_message function was called
    if status_code == 200:
        mock_publish_message.assert_called_once()

    # Ensure the fetch_user and fetch_product functions were called
    mock_fetch_user.assert_called_once_with(req_data["user_id"])
    mock_fetch_product.assert_called_once_with(req_data["product_code"])
