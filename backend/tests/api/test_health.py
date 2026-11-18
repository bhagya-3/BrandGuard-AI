def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)


def test_api_info_endpoint(client):
    response = client.get("/api-info")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)