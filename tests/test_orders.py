from fastapi import status

def _create_and_login_user(client, email, password, admin=False):
    client.post("/auth/create_account", json={
        "name": "Test User",
        "email": email,
        "password": password,
        "admin": admin
    })
    res = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    return res.json()["access_token"]

def test_create_order(client):
    token = _create_and_login_user(client, "user@example.com", "password")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/order/", headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "Order created successfully" in response.json()["Message"]

def test_list_orders_non_admin(client):
    token1 = _create_and_login_user(client, "user1@example.com", "password")
    token2 = _create_and_login_user(client, "user2@example.com", "password")

    # Create an order for user 1
    client.post("/order/", headers={"Authorization": f"Bearer {token1}"})

    # List orders as user 2
    res2 = client.get("/order/", headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == status.HTTP_200_OK
    assert len(res2.json()) == 0

    # List orders as user 1
    res1 = client.get("/order/", headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == status.HTTP_200_OK
    assert len(res1.json()) == 1

def test_list_orders_admin(client):
    token1 = _create_and_login_user(client, "user1@example.com", "password")
    admin_token = _create_and_login_user(client, "admin@example.com", "password", admin=True)

    # Create order for user 1
    client.post("/order/", headers={"Authorization": f"Bearer {token1}"})

    # List orders as admin
    res = client.get("/order/", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) == 1

def test_get_order_by_id(client):
    token1 = _create_and_login_user(client, "user1@example.com", "password")
    token2 = _create_and_login_user(client, "user2@example.com", "password")

    # Create order
    create_res = client.post("/order/", headers={"Authorization": f"Bearer {token1}"})
    order_id = int(create_res.json()["Message"].split()[-1])

    # Get order as owner
    res = client.get(f"/order/{order_id}", headers={"Authorization": f"Bearer {token1}"})
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["id"] == order_id

    # Get order as non-owner (forbidden)
    res_forbidden = client.get(f"/order/{order_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN

def test_cancel_order(client):
    token = _create_and_login_user(client, "user@example.com", "password")
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/order/", headers=headers)
    order_id = int(create_res.json()["Message"].split()[-1])

    cancel_res = client.post(f"/order/{order_id}/cancel", headers=headers)
    assert cancel_res.status_code == status.HTTP_200_OK
    assert cancel_res.json()["order"]["status"] == "CANCELED"

def test_add_order_item_and_finalize(client):
    token = _create_and_login_user(client, "user@example.com", "password")
    headers = {"Authorization": f"Bearer {token}"}

    # Create order
    create_res = client.post("/order/", headers=headers)
    order_id = int(create_res.json()["Message"].split()[-1])

    # Add item
    item_payload = {
        "amount": 2,
        "flavor": "Calabresa",
        "size": "Grande",
        "unit_price": 45.0
    }
    add_res = client.post(f"/order/{order_id}/items", json=item_payload, headers=headers)
    assert add_res.status_code == status.HTTP_201_CREATED
    assert add_res.json()["order"]["price"] == 90.0
    assert len(add_res.json()["order"]["items"]) == 1

    # Finalize order
    finish_res = client.post(f"/order/{order_id}/finish", headers=headers)
    assert finish_res.status_code == status.HTTP_200_OK
    assert len(finish_res.json()) == 1
    assert finish_res.json()[0]["flavor"] == "Calabresa"

def test_delete_order_item(client):
    token = _create_and_login_user(client, "user@example.com", "password")
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/order/", headers=headers)
    order_id = int(create_res.json()["Message"].split()[-1])

    item_payload = {
        "amount": 1,
        "flavor": "Mussarela",
        "size": "Media",
        "unit_price": 35.0
    }
    add_res = client.post(f"/order/{order_id}/items", json=item_payload, headers=headers)
    item_id = add_res.json()["order"]["items"][0]["id"]

    # Delete item
    del_res = client.delete(f"/order/items/{item_id}", headers=headers)
    assert del_res.status_code == status.HTTP_200_OK
    assert del_res.json()["order"]["price"] == 0.0
    assert len(del_res.json()["order"]["items"]) == 0
