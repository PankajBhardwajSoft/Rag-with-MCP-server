from starlette.testclient import TestClient

from mcp_server import build_http_app


def test_root_redirects_to_mcp_endpoint() -> None:
    app = build_http_app()
    client = TestClient(app)

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/mcp"
