# Dashboard Specification — v0.1

**Version:** 0.1
**Status:** Draft (SDD phase)
**Date:** 2026-09-09
**Branch:** `feature/p0-dashboard`
**Owner:** `unified-finance-integration-api`

---

## 1. Objective

Provide a single, presentation-grade, human-facing web page served by the
Unified Finance Integration API at `GET /` that demonstrates the P0
synchronous API-to-simulator invoice flow. The page is the only human UI
exposed to a viewer of the demo; sibling repositories remain invisible.

## 2. User story

> As a non-technical viewer of the local P0 demo, I open one URL
> (`http://localhost:8000/`), see a clear explanation of what is about to
> happen, press one button, and see the invoices the system retrieved — with
> a clear visual state at every moment and a plain-language explanation that
> nothing is being saved.

## 3. Functional requirements

| ID | Requirement |
|---|---|
| FR-D-01 | The dashboard is served at `GET /` by FastAPI in this repository. |
| FR-D-02 | The dashboard consists of a single-page, responsive, vanilla HTML/CSS/JavaScript application served from `app/static/index.html`. |
| FR-D-03 | The browser calls only the existing same-origin endpoint `POST /api/v1/sync/invoices`. No other HTTP call is made by the browser. |
| FR-D-04 | The browser does not call the simulator, does not send any API key, does not read or write cookies, `localStorage`, `sessionStorage`, or IndexedDB. |
| FR-D-05 | No new API endpoint, no CORS configuration, no authentication, no login. |
| FR-D-06 | The user-visible language is Russian. The dashboard title is `Unified Finance`. |
| FR-D-07 | The primary button label is `Синхронизировать счета` and must carry `data-testid="sync-button"`. |
| FR-D-08 | The dashboard exposes stable semantic markers for tests and accessibility tools: `data-testid="dashboard-title"`, `data-testid="sync-status"`, `data-testid="invoice-summary"`, `data-testid="invoice-table"`, `data-testid="p0-disclaimer"`. |
| FR-D-09 | Initial state shows the title, an empty-state instruction, and an enabled button. |
| FR-D-10 | Loading state disables the button, sets `aria-busy="true"` on a status region with `aria-live="polite"`, and renders a non-color-only progress text. |
| FR-D-11 | Success state renders a plain-language success line, dynamic fetched-count card, currencies-count card, last-updated timestamp, and the invoice table. |
| FR-D-12 | Error state renders a plain-language recoverable message; no stack trace, no provider URL, no API key, no raw internal diagnostics. The sync button returns to enabled. |
| FR-D-13 | The invoice table columns (visible to the user) are: invoice ID, customer, amount, currency, invoice date, due date, status. |
| FR-D-14 | The dashboard renders the actual `fetched_count` from the response — never a fixed number. |
| FR-D-15 | Status values are translated to Russian as: `PAID` → `Оплачен`, `UNPAID` → `Не оплачен`, `OVERDUE` → `Просрочен`. Unknown statuses remain safely visible as their raw value (no blank cell). |
| FR-D-16 | The dashboard shows the explicit disclaimer text `Демо P0: счета получаются в реальном времени, но пока не сохраняются.` |

## 4. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-D-01 | The page is responsive at viewport widths from 360 px to 1920 px. |
| NFR-D-02 | Color is never the only state carrier. Every visual state (initial / loading / success / error) is also expressed via text and ARIA. |
| NFR-D-03 | The page works without JavaScript framework: vanilla JS only, no bundler. |
| NFR-D-04 | The page works without any third-party CDN; all assets are bundled with the API repository. |

## 5. Architecture and design decisions

| ID | Decision | Rationale |
|---|---|---|
| AD-D-01 | FastAPI owns the dashboard delivery at `GET /`. | Single repo for backend + presentation keeps Gitflow simple. |
| AD-D-02 | Future implementation uses an **explicit** `GET /` route returning `HTMLResponse(index_html.read_text())`. A catch-all `StaticFiles` mount on `/` is **not** used. | Explicit route avoids mount-order surprises with existing `/health` and `/api/v1/sync/invoices` routes. |
| AD-D-03 | API readiness is shown as an initial UI state — not via a browser-side `/health` request. | Avoids additional browser HTTP traffic; the API is up if the page is up. |
| AD-D-04 | Simulator reachability is communicated **only** as "after a successful sync, provider connectivity was verified." No standalone simulator-health badge is rendered. | Avoids browser-to-simulator cross-origin calls and avoids inventing a new API endpoint that aggregates health. |
| AD-D-05 | No new API endpoint is created. The UI invokes the existing `POST /api/v1/sync/invoices` and consumes the existing success envelope `{status, fetched_count, invoices}` and the existing error envelope `{error}`. | The contract is fixed and audited; the dashboard must not change it. |
| AD-D-06 | No frontend framework, no build step, no package.json, no Node toolchain. | Inventory showed zero JS dependency in the API repo; adding one violates YAGNI (workspace INV-012). |
| AD-D-07 | No pagination UI, no retry/backoff controls, no error-injection controls, no debug panel. | All explicitly out of P0 scope (see §7). |

## 6. Interface contract dependencies

The dashboard depends only on the existing public contract:

- `POST /api/v1/sync/invoices` (no request body, JSON response).
- Success body: `{"status":"success","fetched_count":<int>,"invoices":[Invoice,…]}`.
- Each `Invoice`: `id, contact_name, total_amount, currency, date, due_date, status`.
- Error body: `{"error":"<plain message>"}` with HTTP status 400/500/502/503.
- Status 503 may carry `Retry-After: <seconds>` (forwarded only when numeric).

No other endpoint is required and no contract changes are introduced by this
specification.

## 7. Out of scope (explicit)

- Persistence, database, schema, migration, ORM.
- Login, authentication, sessions, cookies.
- Client-side secrets, API keys in the browser, localStorage/sessionStorage/IndexedDB.
- Browser-to-simulator cross-origin calls, CORS configuration.
- New API endpoint, public test endpoint, query-string error injection.
- Pagination UI, traversal of multiple provider pages.
- Retry / backoff controls, automatic polling, scheduled sync, webhooks.
- Error-injection controls (`simulate_error` query parameter UI, etc.).
- Frontend framework, build tool, package manager, separate frontend repository.
- Dashboard backend in workspace or simulator repositories.
- Claim that the dashboard is "live", "production", "monitored", or "CI-verified" before integration validation has completed.

## 8. Acceptance criteria

| ID | Criterion |
|---|---|
| AC-D-01 | `GET /` returns HTTP 200 with `Content-Type: text/html; charset=utf-8`. |
| AC-D-02 | The HTML body contains `data-testid="dashboard-title"` with the text `Unified Finance`. |
| AC-D-03 | The HTML body contains a button element with `data-testid="sync-button"` and visible label `Синхронизировать счета`. |
| AC-D-04 | The HTML body contains a region with `data-testid="sync-status"` carrying `aria-live="polite"`. |
| AC-D-05 | The HTML body contains the disclaimer `Демо P0: счета получаются в реальном времени, но пока не сохраняются.` inside an element with `data-testid="p0-disclaimer"`. |
| AC-D-06 | Pressing the button issues exactly one `POST /api/v1/sync/invoices` request with empty body and no headers. |
| AC-D-07 | On 200 success, the dashboard renders the success state with `data-testid="invoice-table"` populated by one `<tr>` per returned invoice and a `data-testid="invoice-summary"` block. |
| AC-D-08 | On any non-200, the dashboard renders an error message inside the status region without revealing provider URLs, API keys, or stack traces. |
| AC-D-09 | The dashboard does not call the simulator URL, does not call `/health`, and does not call any URL other than `POST /api/v1/sync/invoices` on its own origin. |
| AC-D-10 | The dashboard contains no references to `localStorage`, `sessionStorage`, `IndexedDB`, or cookies. |
| AC-D-11 | The dashboard renders no fixed invoice count assertion; the displayed count is whatever the API returns. |
| AC-D-12 | The dashboard works correctly when the API returns 1 invoice, 0 invoices, and 100 invoices (visually verified manually after TDD stage). |
| AC-D-13 | All existing API tests in `tests/test_sync.py` and `tests/test_health.py` continue to pass. |

## 9. Privacy and security

- The dashboard never receives, embeds, or displays the value of `PROVIDER_API_KEY`.
- The browser never sends `X-API-Key` or any provider credential.
- The dashboard never embeds provider URLs, internal hostnames, or environment names in user-visible text.
- Error messages in the UI use plain language and do not propagate server-side exception messages verbatim.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Misclaim of "production-ready" or "live E2E" | Specification explicitly forbids such claims until integration validation has completed (see §11). |
| Route conflict between `GET /` and existing API routes | Explicit `GET /` route is added; existing `/health` and `POST /api/v1/sync/invoices` are matched first. |
| Accidental introduction of a frontend framework | CI lint step (existing) will catch additional dependencies in `requirements.txt` because none are added. |
| Accidental addition of new API endpoint | Specification §7 and AC-D-09 prohibit it; review checklist includes endpoint count check. |

## 11. Presentation claims allowed only after validation

The following claims are **safe** in any presentation:

- "The P0 demo exposes a single-page dashboard at `http://localhost:8000/`."
- "The dashboard calls the existing `POST /api/v1/sync/invoices` endpoint."
- "P0 is stateless — no invoices are persisted."
- "The dashboard is in Russian for end-user clarity."
- "The dashboard page asset is delivered from `app/static/index.html` through the API."

The following claims are **forbidden** until integration validation has
completed (workplace smoke runner green, API tests green, manual browser
review):

- "Live E2E has been run."
- "Pagination traversal is implemented."
- "Live cross-service 429 E2E has been validated."
- "A dashboard fix has been merged and released."
- Any timestamp, screenshot, or run-output claim that has not been observed.

## 12. Traceability

| Source | Destination |
|---|---|
| Workspace INV-005 (SDD) | This document. |
| Workspace INV-011 (TDD) | TDD plan in `dashboard-plan.md`. |
| Workspace INV-012 (KISS/YAGNI) | §5 AD-D-06 (no framework); §7 (no persistence / pagination / retry). |
| Workspace INV-015 (data integrity) | §6 (uses only validated API contract). |
| Workspace INV-016 (repository ownership) | §5 AD-D-01 (dashboard lives in API repo only). |
| Workspace INV-019 (explicit approval gates) | Stage boundary before commit and before merge. |
| API contract `docs/contracts/invoice-sync-v0.1.md` | §6 (interface contract dependencies). |
