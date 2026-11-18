def test_openapi_schema_is_available(client):
    response = client.get("/openapi.json")

    # Your main.py enables documentation only when DEBUG is true.
    if response.status_code == 200:
        schema = response.json()

        assert "paths" in schema
        assert "info" in schema
    else:
        assert response.status_code in (404, 403)