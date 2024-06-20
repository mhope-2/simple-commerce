import pytest


test_data = [
    ("7c11e1ce2741", 200, {"first_name": "John", "id": "7c11e1ce2741", "last_name": "Doe"}),
    ("e6f24d7d1c7e", 500, {"detail": "Internal Server Error"}),
    ("unknownID", 404, {"detail": "User not found"}),
]


@pytest.mark.parametrize("id, status_code, res_data", test_data)
@pytest.mark.asyncio
async def test_retrieve_user_by_id(client, id, status_code, res_data):
    res = client.get(f"/users/{id}/")
    assert res.status_code == status_code
    assert res.json() == res_data
