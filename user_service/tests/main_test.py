import pytest


@pytest.mark.parametrize("id, status_code, res_data", [
    ("7c11e1ce2741", 200, {'first_name': 'John', 'id': '7c11e1ce2741', 'last_name': 'Doe'}),
    ("userX", 404, {"detail": "User not found"}),
])
def test_retrieve_user(client, id, status_code, res_data):
    res = client.get(f"/users/{id}")
    assert res.status_code == status_code
    assert res.json() == res_data
