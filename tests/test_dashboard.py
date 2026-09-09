from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_get_returns_html() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_dashboard_contains_required_semantic_markers() -> None:
    response = client.get("/")
    body = response.text

    for marker in (
        'data-testid="dashboard-title"',
        'data-testid="sync-button"',
        'data-testid="sync-status"',
        'data-testid="invoice-summary"',
        'data-testid="invoice-table"',
        'data-testid="p0-disclaimer"',
    ):
        assert marker in body


def test_dashboard_uses_required_copy() -> None:
    body = client.get("/").text

    assert '<html lang="en">' in body
    assert "Unified Finance" in body
    assert "Sync Invoices" in body
    assert "P0 Demo: Invoices are fetched in real time but are not persisted." in body


def test_dashboard_has_no_forbidden_client_tokens() -> None:
    body = client.get("/").text

    for token in (
        "simulator:5000",
        "/health",
        "PROVIDER_API_KEY",
        "X-API-Key",
        "localStorage",
        "sessionStorage",
        "IndexedDB",
    ):
        assert token not in body


def test_dashboard_status_badges_and_safe_dom_manipulation() -> None:
    body = client.get("/").text

    for class_name in (
        "status-badge",
        "status-badge--paid",
        "status-badge--unpaid",
        "status-badge--overdue",
        "status-badge--unknown",
    ):
        assert class_name in body

    for label in ("Paid", "Unpaid", "Overdue"):
        assert label in body

    assert 'document.createElement("span")' in body
    assert "textContent" in body
    assert "innerHTML" not in body
    assert "insertAdjacentHTML" not in body
