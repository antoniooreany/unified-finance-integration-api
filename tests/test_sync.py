import pytest
from fastapi.testclient import TestClient
import respx
import httpx
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("PROVIDER_BASE_URL", "http://localhost:5000")
    monkeypatch.setenv("PROVIDER_API_KEY", "test-key")

def test_sync_invoices_success_returns_normalized_response(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        route = respx_mock.get("http://localhost:5000/api/v1/invoices").respond(
            status_code=200,
            json={
                "invoices": [
                    {
                        "id": "INV-1",
                        "contact_name": "Test",
                        "total_amount": 100.0,
                        "currency": "USD",
                        "date": "2023-01-01",
                        "due_date": "2023-01-15",
                        "status": "PAID"
                    }
                ]
            }
        )
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 200
        assert route.called
        data = response.json()
        assert data["status"] == "success"
        assert data["fetched_count"] == 1
        assert data["invoices"][0]["id"] == "INV-1"

def test_sync_invoices_provider_401_mapping(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(status_code=401)
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 500
        assert response.json() == {"error": "Provider configuration error"}

def test_sync_invoices_provider_429_mapping_and_valid_retry_after_forwarding(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(
            status_code=429, headers={"Retry-After": "5"}
        )
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 503
        assert response.headers.get("Retry-After") == "5"
        assert response.json() == {"error": "Provider temporarily unavailable"}

def test_sync_invoices_invalid_missing_non_numeric_retry_after_is_not_forwarded(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(
            status_code=429, headers={"Retry-After": "invalid"}
        )
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 503
        assert "Retry-After" not in response.headers

        # Test missing Retry-After
        respx_mock.clear()
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(status_code=429)
        response2 = client.post("/api/v1/sync/invoices")
        assert response2.status_code == 503
        assert "Retry-After" not in response2.headers

def test_sync_invoices_provider_500_mapping(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(status_code=500)
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 502
        assert response.json() == {"error": "Provider service error"}

def test_sync_invoices_timeout_mapping(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        respx_mock.get("http://localhost:5000/api/v1/invoices").mock(side_effect=httpx.TimeoutException)
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 503
        assert response.json() == {"error": "Provider unavailable"}

def test_sync_invoices_connection_failure_mapping(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        respx_mock.get("http://localhost:5000/api/v1/invoices").mock(side_effect=httpx.ConnectError("error"))
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 503
        assert response.json() == {"error": "Provider unavailable"}

def test_sync_invoices_malformed_json_mapping(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(
            status_code=200, content=b"{malformed json"
        )
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 502
        assert response.json() == {"error": "Invalid provider response"}

def test_sync_invoices_missing_non_list_invoices_mapping(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        # Missing invoices key
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(
            status_code=200, json={"other_key": []}
        )
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 502
        assert response.json() == {"error": "Invalid provider response"}

        # Invoices is not a list
        respx_mock.clear()
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(
            status_code=200, json={"invoices": "not a list"}
        )
        response2 = client.post("/api/v1/sync/invoices")
        assert response2.status_code == 502

def test_sync_invoices_strict_invoice_validation(mock_env):
    with respx.mock(assert_all_mocked=True) as respx_mock:
        # Missing required field "currency"
        respx_mock.get("http://localhost:5000/api/v1/invoices").respond(
            status_code=200, json={
                "invoices": [
                    {
                        "id": "INV-1",
                        "contact_name": "Test",
                        "total_amount": 100.0,
                        "date": "2023-01-01",
                        "due_date": "2023-01-15",
                        "status": "PAID"
                    }
                ]
            }
        )
        response = client.post("/api/v1/sync/invoices")
        assert response.status_code == 502
        assert response.json() == {"error": "Invalid provider response"}

def test_sync_invoices_proof_mocked_network(mock_env):
    with respx.mock(assert_all_mocked=True):
        # Do not mock the endpoint. The client will try to call it and respx will block it.
        with pytest.raises(Exception):
            client.post("/api/v1/sync/invoices")
