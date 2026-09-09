# Dashboard Implementation Plan — v0.1

**Version:** 0.1
**Status:** Draft (SDD phase)
**Branch:** `feature/p0-dashboard`
**Owner:** `unified-finance-integration-api`

---

## 1. Scope

This plan implements the requirements in `dashboard-spec.md` (this directory)
in a single future commit using strict TDD (red → green → refactor).

## 2. File-level implementation plan

The implementation stage will modify or create exactly the following files
within this repository:

| Path | Action | Purpose |
|---|---|---|
| `app/main.py` | **modify** | Add explicit `GET /` route returning `HTMLResponse`. Order: declare `/health` and `POST /api/v1/sync/invoices` first, then `GET /` last, so existing routes keep priority. |
| `app/static/index.html` | **create** | Single-file vanilla HTML containing inline `<style>` and `<script>`. Carries all required `data-testid` markers. |
| `tests/test_dashboard.py` | **create** | Pytest module asserting `GET /` returns 200 + `text/html` and contains the required `data-testid` markers. |
| `README.md` | **modify** | Add one paragraph documenting the dashboard route. |

**Files explicitly NOT touched in this stage:**

- `Dockerfile`, `.dockerignore`, `requirements.txt`, `pyproject.toml`
- `.github/workflows/ci.yml`
- `app/config.py`, `app/provider.py`, `app/schemas.py`
- `tests/test_sync.py`, `tests/test_health.py`
- `compose.yaml` (workspace)
- Any sibling repository or contract file

## 3. Route and module shape

`app/main.py` after the change (logical shape, no whitespace shown):

```python
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from app.provider import fetch_invoices
from app.schemas import SyncResponse

app = FastAPI()

# Existing exception handler (unchanged)
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException): ...

# Existing routes (unchanged, declared first so they match before GET /)
@app.get("/health")
def health(): ...

@app.post("/api/v1/sync/invoices", response_model=SyncResponse)
async def sync_invoices(): ...

# New route (declared last)
INDEX_HTML = Path(__file__).resolve().parent / "static" / "index.html"

@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")
```

The explicit `GET /` route returns the file content as a string. No
`StaticFiles` mount is introduced; no catch-all root static handler is
installed.

## 4. `app/static/index.html` outline

Single file. Required structure (semantic markers are required by tests):

```
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Unified Finance</title>
  <style>...</style>
</head>
<body>
  <header>
    <h1 data-testid="dashboard-title">Unified Finance</h1>
    <p>Получайте счета от поставщиков в одном месте.</p>
  </header>

  <section data-testid="invoice-summary" hidden>
    <div>Получено счетов: <span data-testid="summary-count"></span></div>
    <div>Валют: <span data-testid="summary-currencies"></span></div>
    <div>Последнее обновление: <span data-testid="summary-updated"></span></div>
  </section>

  <button data-testid="sync-button" type="button">Синхронизировать счета</button>

  <div data-testid="sync-status" role="status" aria-live="polite" aria-busy="false">
    Готово к синхронизации.
  </div>

  <table data-testid="invoice-table" hidden>
    <caption class="visually-hidden">Синхронизированные счета</caption>
    <thead>
      <tr>
        <th scope="col">№ счёта</th>
        <th scope="col">Клиент</th>
        <th scope="col">Сумма</th>
        <th scope="col">Валюта</th>
        <th scope="col">Дата счёта</th>
        <th scope="col">Срок оплаты</th>
        <th scope="col">Статус</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>

  <p data-testid="p0-disclaimer">
    Демо P0: счета получаются в реальном времени, но пока не сохраняются.
  </p>

  <script>
    // fetch('http://localhost:8000/api/v1/sync/invoices', { method: 'POST' })
    // then render success / error states into the markers above.
  </script>
</body>
</html>
```

JavaScript behavior (full implementation in the future code stage):

- Click handler on the sync button:
  - Sets `aria-busy="true"` on the status region; disables the button; sets
    visible text to `Получаем и обрабатываем счета…`.
  - Issues `fetch('/api/v1/sync/invoices', { method: 'POST' })` with empty
    body and **no** headers.
  - On `response.ok` (HTTP 200): reads JSON, renders summary cards, hides
    the table placeholder, fills `<tbody>` with one row per invoice,
    shows the table and summary, sets status text to a plain-language
    success line.
  - On non-OK response: sets status text to a plain-language recoverable
    message, leaves the table hidden if previously hidden, does **not**
    display response body verbatim.
  - On network failure: same error path.
- Status translation table (Russian):
  - `PAID` → `Оплачен`
  - `UNPAID` → `Не оплачен`
  - `OVERDUE` → `Просрочен`
  - any other value: rendered as-is (no empty cell, no fallback text).
- Currency formatting: use `Intl.NumberFormat('ru-RU', { style: 'currency', currency: code })`.
- Date formatting: keep ISO `YYYY-MM-DD` string as-is for clarity.
- No `localStorage`, `sessionStorage`, `IndexedDB`, or cookies touched.

## 5. TDD red → green → refactor sequence

### 5.1 Red — write the test first

Create `tests/test_dashboard.py` with at minimum:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_get_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_dashboard_contains_required_semantic_markers():
    response = client.get("/")
    body = response.text
    assert 'data-testid="dashboard-title"' in body
    assert 'data-testid="sync-button"' in body
    assert 'data-testid="sync-status"' in body
    assert 'data-testid="invoice-summary"' in body
    assert 'data-testid="invoice-table"' in body
    assert 'data-testid="p0-disclaimer"' in body


def test_dashboard_button_label_is_russian():
    response = client.get("/")
    assert "Синхронизировать счета" in response.text


def test_dashboard_disclaimer_text_present():
    response = client.get("/")
    assert "Демо P0: счета получаются в реальном времени, но пока не сохраняются." in response.text


def test_dashboard_no_simulator_health_request():
    # Static analysis: ensure HTML does not reference simulator URL or
    # /health path or PROVIDER_API_KEY.
    body = client.get("/").text
    forbidden = ["simulator:5000", "/health", "PROVIDER_API_KEY", "X-API-Key",
                 "localStorage", "sessionStorage", "IndexedDB"]
    for token in forbidden:
        assert token not in body, f"forbidden token {token!r} present in dashboard"
```

Run `pytest tests/test_dashboard.py -q` and observe **failure** for every
test (no `GET /` route, no `index.html` file).

### 5.2 Green — minimal implementation

1. Add `app/static/index.html` with a minimal placeholder containing all
   required `data-testid` markers and the Russian labels.
2. Add the `GET /` route to `app/main.py` returning
   `INDEX_HTML.read_text(...)`.

Run `pytest tests/test_dashboard.py -q` and observe all tests **pass**.

### 5.3 Green — full UI implementation

1. Implement the full HTML structure (header, summary section, button,
   status region, table, disclaimer).
2. Implement CSS (inline `<style>`) for responsive layout, accessible
   focus states, and color-not-only state indicators.
3. Implement JS (`<script>` block) with the four states and the
   status-translation table.
4. Re-run `pytest tests/test_dashboard.py -q` — must remain green.

### 5.4 Refactor and full-suite verification

1. Refactor for readability (constants for status translations, helper
   functions inside the inline script).
2. Run the full API test suite: `.venv/Scripts/python.exe -m pytest -q` —
   must remain green; existing `test_sync.py` and `test_health.py` are
   unaffected.

### 5.5 Regression via workspace smoke runner

After the implementation PR is merged into `develop`, run the workspace
smoke runner:

```
python scripts/smoke_test.py
```

(From `integration-workspace`.)

This is the integration-level regression. It is **not** part of the
implementation commit itself, but is required before claiming "the
dashboard works end-to-end."

### 5.6 Manual browser review checklist

Run the stack with `docker compose up`, open `http://localhost:8000/`, and
confirm:

1. Initial render is correct.
2. Click triggers loading state.
3. Success render shows table and summary cards.
4. Keyboard navigation through the button and table headers.
5. Screen-reader announcement of status changes (`aria-live="polite"`).

Error-state behavior is verified by implementation review of the four
states and must not expose raw stack traces, provider URLs, or API keys in
the user-visible message. Live error-path E2E (forcing a real
provider/simulator failure end-to-end) remains future P1 work and is
**not** part of this dashboard milestone.

Only after steps 1–5 succeed may presentation claims be made.

## 6. Local and CI verification plan

| Stage | Local command | CI command |
|---|---|---|
| Static | `python -m pytest tests/test_dashboard.py -q` | (covered by existing `pytest -v` job) |
| Full API suite | `.venv/Scripts/python.exe -m pytest -q` | `python -m pytest -v` |
| Lint | `ruff check .` (if installed) | `ruff-action@v3` |
| Docker build | `docker build -t ufi-api:dev .` | `docker-smoke-test` job |
| Integration | `python scripts/smoke_test.py` (workspace) | not currently in workspace CI |

## 7. Gitflow and CI gates

- Feature branch: `feature/p0-dashboard` based on `develop` @ `70324a05ae2f7ef21b0de0958e66093834291d7b`.
- Commit messages follow Conventional Commits (workspace INV-007):
  - Implementation commit: `feat(api): add static P0 dashboard at /`
- The implementation commit is **not** the SDD-only commit. SDD artifacts
  may land in a separate commit (`docs(api): add P0 dashboard SDD`).
- PR target: `develop`.
- CI gate (workspace INV-014 + API repo CI): lint, pytest, docker-smoke-test must pass before merge.
- Manual review: a reviewer verifies AC-D-01 through AC-D-13 against the
  live `http://localhost:8000/` page before approving.

## 8. Sequencing summary

| # | Action | Stage |
|---|---|---|
| 1 | Create the three SDD docs (`dashboard-spec.md`, `dashboard-plan.md`, `dashboard-tasks.md`) | **Current — SDD stage** |
| 2 | Commit SDD docs (separate commit) | Pending approval |
| 3 | Create `tests/test_dashboard.py`, run red | Future — TDD stage |
| 4 | Add minimal `app/static/index.html` + `GET /` route, run green | Future — TDD stage |
| 5 | Implement full dashboard HTML/CSS/JS | Future — TDD stage |
| 6 | Run full API `pytest -q` | Future — TDD stage |
| 7 | Update `README.md` with one paragraph | Future — TDD stage |
| 8 | Conventional-commit `feat(api): add static P0 dashboard at /` (implementation commit) | Pending approval |
| 9 | Push and open PR to `develop` | Pending approval |
| 10 | CI green + reviewer manual browser check | Pending approval |
| 11 | Merge to `develop` | Pending approval |
| 12 | Run workspace smoke runner as integration regression | Future |
| 13 | Make safe presentation claims only after step 12 | Future |
