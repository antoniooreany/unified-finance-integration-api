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

def test_dashboard_has_minimal_primary_navigation() -> None:
    body = client.get("/").text

    assert body.count("<nav") == 1
    assert 'aria-label="Primary navigation"' in body

    assert 'href="#dashboard"' in body
    assert ">Dashboard<" in body

    assert 'href="#invoices"' in body
    assert ">Invoices<" in body

    assert 'href="/docs"' in body
    assert ">API Docs<" in body

    assert 'id="dashboard"' in body
    assert 'id="invoices"' in body

    assert body.count("<button") == 1
    assert body.count("fetch(") == 1

def test_dashboard_has_expandable_invoice_details() -> None:
    body = client.get("/").text

    assert "Actions" in body
    assert "View details" in body
    assert "Hide details" in body
    assert "aria-expanded" in body
    assert "aria-controls" in body
    assert "invoice-details-" in body
    assert "colspan = 8" in body or 'colspan="8"' in body
    assert 'document.createElement("button")' in body
    assert 'document.createElement("tr")' in body
    assert 'document.createElement("td")' in body
    assert "textContent" in body
    assert "innerHTML" not in body
    assert "insertAdjacentHTML" not in body
    assert body.count("fetch(") == 1
    assert body.count("<button") == 1

def test_dashboard_renders_structured_invoice_details_card() -> None:
    body = client.get("/").text

    assert "invoice-details-card" in body
    assert "Invoice details" in body
    assert "invoice-details-grid" in body
    assert "invoice-detail" in body
    assert "invoice-detail-label" in body
    assert "invoice-detail-value" in body
    assert "Invoice number" in body
    assert "Customer" in body
    assert "Amount" in body
    assert "Currency" in body
    assert "Invoice date" in body
    assert "Due date" in body
    assert "Status" in body
    assert 'document.createElement("div")' in body
    assert "textContent" in body
    assert "grid-template-columns" in body
    assert "@media" in body
    assert "innerHTML" not in body
    assert "insertAdjacentHTML" not in body
    assert body.count("fetch(") == 1
    assert body.count("<button") == 1

def test_dashboard_styles_invoice_details_card_without_inline_styles() -> None:
    body = client.get("/").text

    assert "invoice-details-heading" in body
    assert "invoice-detail-value--amount" in body
    assert "grid-template-columns: repeat(3, 1fr)" in body
    assert "@media (max-width: 600px)" in body
    assert "@media (max-width: 420px)" in body
    assert "grid-template-columns: 1fr" in body
    assert "heading.style." not in body
    assert "valDiv.style." not in body
    assert "innerHTML" not in body
    assert "insertAdjacentHTML" not in body
    assert body.count("fetch(") == 1
    assert body.count("<button") == 1

def test_dashboard_omits_nonfunctional_navigation_controls() -> None:
    body = client.get("/").text

    assert 'href="#dashboard"' not in body
    assert 'href="#invoices"' not in body
    assert ">Dashboard<" not in body
    assert ">Invoices<" not in body
    assert ">API Docs<" not in body
    assert "Unified Finance" in body
    assert "Sync Invoices" in body
    assert body.count("<button") == 1
    assert body.count("fetch(") == 1
    assert "innerHTML" not in body
    assert "insertAdjacentHTML" not in body
