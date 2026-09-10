## Why

The backend authenticates to every Google Cloud API it calls (Discovery Engine REST endpoints and the `discoveryengine` client library) exclusively through Application Default Credentials (`google.auth.default()`), and the README only documents and the project has only been exercised against user credentials (`gcloud auth application-default login`). Enterprises that federate an external IdP (Okta, Azure AD, ADFS, etc.) via Workforce Identity Federation (WIF) authenticate through an `external_account` credential config instead of a user or service-account principal. Nothing today confirms that the app's token acquisition, refresh, and quota-project resolution logic actually succeeds when the active ADC principal is a WIF identity, so a WIF-based customer could adopt this explorer and silently hit auth failures that never show up in the current ADC-only validation path.

## What Changes

- Add a `wif-authentication` capability spec that states every Google Cloud API call the backend makes (the `api-explorer` routes that build headers from `google.auth.default()` credentials, and `SearchClient`'s `discoveryengine.SearchServiceClient`) SHALL succeed identically when the resolved ADC principal is a Workforce Identity Federation `external_account` identity as when it is a standard user or service-account identity.
- Add requirements covering: initial token acquisition for a WIF principal, credential refresh when a WIF-sourced token is expired/invalid, and `X-Goog-User-Project` quota-project header resolution when WIF's `default()` call returns no project (WIF ADC frequently has no associated project, unlike user/service-account ADC).
- Add a read-only `GET /api-explorer/auth-status` backend endpoint that introspects the active ADC credential object and classifies it (WIF, Workload Identity Federation, service account, user account, attached service account, impersonated), and a small UI badge in the config sidebar that displays that classification — so the demo can actually show a WIF identity is in effect, not just claim it works.
- Add a documented validation procedure (manual, since it requires a real workforce pool/provider) for configuring ADC against a WIF credential config and exercising every backend endpoint against it.
- Document WIF-based ADC setup as a supported alternative to `gcloud auth application-default login` in the README.
- No behavioral code change to the existing API-explorer routes is assumed up front; if validation surfaces a WIF-specific defect (e.g. a hard requirement on `adc_project` being non-empty), fix it as part of this change's tasks.

## Capabilities

### New Capabilities
- `wif-authentication`: Requirements that the backend's ADC-based Google Cloud authentication (used by every `api-explorer` route and by `SearchClient`) functions correctly — token acquisition, refresh, and quota-project resolution — when the active credential is a Workforce Identity Federation `external_account` identity, plus a way to observe which identity kind is actually active, plus the validation scenarios that prove it.

### Modified Capabilities
(none — no existing spec covers authentication today)

## Impact

- `backend/api/routes/api_explorer.py`: every route calling `default()` / `credentials.refresh()` / building the `Authorization` and `X-Goog-User-Project` headers (`get_engine_details`, `web_grounding_search`, `get_engine_data_stores`, `list_assistants`, `list_agents`, `get_agent`, `stream_assist`); new `auth-status` route added.
- `backend/clients/search_client.py`: `SearchClient.__init__` constructing `discoveryengine.SearchServiceClient`, which resolves ADC internally.
- `frontend/components/ConfigSidebar.tsx`: new auth-status badge reading the new endpoint.
- `README.md`: ADC setup instructions gain a WIF-specific path.
- No breaking changes; purely additive validation, one read-only endpoint, one UI badge, and doc updates, with bugfixes only if validation finds a real defect.
</content>
