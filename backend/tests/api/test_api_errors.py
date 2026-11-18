def test_unknown_endpoint_returns_404(client):
    response = client.get("/this-endpoint-does-not-exist")

    assert response.status_code == 404


def test_invalid_http_method(client):
    response = client.delete("/health")

    assert response.status_code in (405, 404)