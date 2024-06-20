import pytest


test_data = [
    ("7c11e1ce2741", 200, {"first_name": "John", "id": "7c11e1ce2741", "last_name": "Doe"}),
    ("unknownID", 404, {"detail": "User not found"}),
]


@pytest.mark.parametrize("id, status_code, res_data", test_data)
@pytest.mark.asyncio
async def test_retrieve_user_by_id(client, id, status_code, res_data):
    res = client.get(f"/users/{id}/")
    assert res.status_code == status_code
    assert res.json() == res_data


@pytest.mark.parametrize("toggle, status_code, response", [
    (True, 200, {"id": "e6f24d7d1c7e", "first_name": "Jane", "last_name": "Doe"}),
    (False, 500, {"detail": "Internal Server Error"}),
])
@pytest.mark.asyncio
async def test_retrieve_user_by_id_toggle(client, toggle, status_code, response):
    res = client.get(f"/users/e6f24d7d1c7e/")
    assert res.status_code == status_code
    assert res.json() == response

