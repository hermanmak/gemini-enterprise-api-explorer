## Context

The backend never builds its own credential objects. Every `api-explorer` route calls `google.auth.default()` to get whatever ADC principal is active in the process environment, then does:

```python
credentials, adc_project = default()
if not credentials.valid:
    credentials.refresh(AuthRequest())
quota_project = adc_project if use_adc_quota else project_number
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "X-Goog-User-Project": quota_project,
    ...
}
```

`SearchClient` never touches credentials directly — it hands a `ClientOptions(api_endpoint=...)` to `discoveryengine.SearchServiceClient()`, which resolves ADC internally via the same `google-auth` machinery.

`google-auth` already supports three ADC shapes: authorized-user (`gcloud auth application-default login`), service-account key JSON, and `external_account` (Workforce/Workload Identity Federation). The library returns an `google.auth.identity_pool.Credentials` (or `google.auth.external_account_authorized_user.Credentials` for the 3P-token flow) object from `default()` when `GOOGLE_APPLICATION_CREDENTIALS` points at a WIF credential-config JSON, or when `gcloud auth application-default login --login-config=<config>` was used. The app's code treats whatever `default()` returns as an opaque `Credentials` duck-type (`.valid`, `.refresh()`, `.token`) — it never branches on credential type today.

The one place this app-specific code makes an assumption that could break under WIF: `adc_project`. For authorized-user and service-account ADC, `default()` usually returns a project id (or `None` if not configured). For WIF `external_account` credentials, `default()` almost always returns `adc_project = None` unless the credential config JSON explicitly sets `quota_project_id`, because workforce identities aren't tied to a single GCP project the way a service account is. Every route already guards this with `use_adc_quota` (falls back to the user-supplied `project_number` when the caller doesn't want ADC's project), but the `use_adc_quota=True` path would silently send `X-Goog-User-Project: None`/omit correct quota attribution if `adc_project` is empty for a WIF principal — this is the one behavior genuinely worth pinning in a spec and checking by hand.

## Goals / Non-Goals

**Goals:**
- State, as testable requirements, that every backend call site sourcing credentials from `google.auth.default()` (all `api-explorer` routes plus `SearchClient`) succeeds when the resolved principal is a WIF `external_account` identity.
- Pin the one WIF-specific edge case that differs from user/service-account ADC: quota-project resolution when ADC reports no project.
- Provide a concrete, repeatable manual validation procedure, since automated CI has no workforce pool/provider to authenticate against.
- Make the active ADC identity kind (WIF or otherwise) directly observable from the UI, so demonstrating WIF actually works doesn't rely on trusting an unobservable server environment variable.

**Non-Goals:**
- Letting the UI collect, paste, or transmit any credential material (tokens, key files, credential-config JSON) — the badge is read-only introspection of whatever ADC the backend host already has; entering/overriding credentials from the browser is a separate, not-yet-decided feature.
- Setting up or provisioning an actual Workforce Identity Federation pool/provider/IdP (that's an out-of-band prerequisite the validator performs once, documented but not automated here).
- OAuth/end-user-auth flows — out of scope per the README's existing ADC-only stance.

## Decisions

- **Treat WIF as "just another ADC credential type," not a new integration.** The code already only calls `.valid`, `.refresh()`, `.token` — the generic `google.auth.credentials.Credentials` interface every ADC type implements. Alternative considered: add a code path that detects `external_account` credentials and handles them specially. Rejected — no evidence today of a divergence beyond `adc_project`, and adding untested branching would be speculative.
- **Fix the `adc_project` fallback if validation shows it breaks quota attribution.** If a WIF-sourced `default()` returns `adc_project=None` while `use_adc_quota=True`, the route must fall back to the user-configured `project_number` instead of sending an empty/`None` quota-project header. Alternative considered: require the WIF credential config to always set `quota_project_id`. Rejected — that pushes an implementation detail onto every WIF setup instead of handling it once in code.
- **Manual validation, not a mocked unit test, for the credential-acquisition scenarios.** `google-auth`'s `external_account` flow requires a live token exchange against a real workforce pool/provider; mocking `google.auth.default()` to return a fake `external_account`-shaped object would only prove the app doesn't crash on the right duck type, not that real WIF tokens work end-to-end. Alternative considered: unit-test with `google.auth.identity_pool.Credentials` constructed from a fixture. Kept as a *supplementary* check (validates the duck-typing assumption), but the spec's authoritative scenarios require exercising real endpoints.
- **Classify credentials with `isinstance` against `google-auth`'s own credential classes, not by hand-parsing tokens.** `google.auth.external_account.Credentials` (base of `identity_pool.Credentials`) already exposes `.is_workforce_pool` and `.info["audience"]`; `external_account_authorized_user.Credentials` is unconditionally WIF (the browser sign-in flow); `service_account.Credentials` exposes `.service_account_email`; `impersonated_credentials.Credentials` wraps a `._source_credentials` and exposes `.service_account_email` for the target. Alternative considered: regex-parsing the audience string ourselves. Rejected — the library already computes and exposes exactly this distinction; re-deriving it risks drifting from `google-auth`'s own definition of "workforce pool."

## Risks / Trade-offs

- [No workforce pool available in this environment to run live validation] → Validation tasks are documented as a manual procedure for whoever owns a GCP org with Workforce Identity Federation configured; the spec's scenarios are still normative and checkable by anyone with such an org, and a supplementary unit test on the duck-typed refresh/token path runs without one.
- [`adc_project` fallback fix, if needed, touches every route in `api_explorer.py`] → Small, mechanical, identical change per call site (already-existing `use_adc_quota` conditional gets an added empty-string/`None` guard); no interface change.
- [WIF token lifetimes can be shorter than service-account tokens, increasing refresh frequency] → Already handled generically by the existing `if not credentials.valid: credentials.refresh(...)` check before every call; no per-request caching to invalidate.
- [Auth-status endpoint accidentally leaks sensitive material] → The response only ever includes credential-class name, `.is_workforce_pool`-derived label, the audience/pool path or service-account email as `principal`, and `adc_project` — never `credentials.token` or any refresh/secret material; enforced by keeping the classification function's return values to exactly those fields.

## Migration Plan

Purely additive (new spec + validation docs, optional small guard fix). No rollback concerns beyond reverting the guard fix if it regresses non-WIF ADC behavior, which the existing non-WIF manual smoke test (list-agents/search with standard ADC) already covers.
</content>
