## 1. WIF environment setup (manual, one-time)

- [ ] 1.1 Provision or reuse a Workforce Identity Federation pool + provider in a GCP org with Discovery Engine/Gemini Enterprise access, and generate a WIF credential-config JSON for a workforce identity that has the necessary IAM roles.
- [ ] 1.2 Configure local ADC against that credential config (`gcloud auth application-default login --login-config=<config>` or `GOOGLE_APPLICATION_CREDENTIALS=<config>`), and confirm `gcloud auth application-default print-access-token` succeeds.
- [ ] 1.3 Inspect `google.auth.default()` output for this WIF principal (credential type, `.valid`, and whether `adc_project` is populated) to confirm the assumption in design.md before running scenario checks.

## 2. Validate existing routes against a WIF identity

- [ ] 2.1 With WIF-based ADC active, exercise `list-agents`, `list-assistants`, `get-agent`, `engine-details`, `engine-data-stores`, and `web-grounding-search` and confirm each returns a successful response (per "Google Cloud API calls succeed with a WIF identity").
- [ ] 2.2 Exercise `stream-assist` directly and via the `deep-research` plan/run flow with WIF-based ADC and confirm both complete (per the same requirement).
- [ ] 2.3 Exercise `SearchClient.search` (via a search-backed route) with WIF-based ADC and confirm results return successfully.
- [ ] 2.4 Force an expired/invalid credential state (e.g. wait out token TTL or manually invalidate) and confirm the affected route refreshes the WIF credential and completes the request (per "Expired WIF credentials are refreshed before use").

## 3. Fix and verify quota-project fallback

- [ ] 3.1 With `use_adc_quota=True` and the WIF principal's `adc_project` empty, confirm whether the current code sends an empty/`None` `X-Goog-User-Project` header; if so, add a fallback to `project_number` in each affected route in `backend/api/routes/api_explorer.py`.
- [ ] 3.2 Re-run the affected routes with `use_adc_quota=True` under WIF ADC and confirm `X-Goog-User-Project` is always a non-empty value (falls back correctly per "Quota-project resolution tolerates a WIF principal with no ADC project").
- [ ] 3.3 Re-run the same routes with `use_adc_quota=True` under standard user/service-account ADC to confirm the fallback change does not alter existing non-WIF behavior.

## 4. Documentation

- [ ] 4.1 Add a "Workforce Identity Federation" subsection to README.md's ADC setup section documenting the WIF login-config / `GOOGLE_APPLICATION_CREDENTIALS` setup path (per "WIF-based ADC setup is documented").
- [ ] 4.2 Record the validation results (which routes were exercised, any defects found and fixed) in the change's proposal or a short results note for future reference.

## 5. Auth-status visibility feature (backend + UI)

- [x] 5.1 Add `GET /api-explorer/auth-status` to `backend/api/routes/api_explorer.py`: call `default()`, refresh if invalid, classify the credential via `isinstance` checks against `google.auth.external_account_authorized_user.Credentials`, `google.auth.external_account.Credentials` (`.is_workforce_pool`), `google.oauth2.service_account.Credentials`, `google.auth.compute_engine.Credentials`, `google.auth.impersonated_credentials.Credentials`, and `google.oauth2.credentials.Credentials`, and return `{credential_type, credential_label, principal, adc_project, valid, success}` (or `{error, success: false}` on failure).
- [x] 5.2 Add a small auth-status badge to `frontend/components/ConfigSidebar.tsx` that fetches the endpoint once on mount and renders `credential_label` (plus `adc_project`/`principal` as secondary detail), with a distinct visual state for the failure case.
- [x] 5.3 Smoke-test the endpoint against whatever ADC is actually available (this sandbox resolves to a user-account credential) and confirm the label matches the resolved credential type; visually confirm the badge renders in the running frontend.
- [x] 5.4 Resolve `principal` to an actual account identifier, not just a pool audience path: decode the `email` claim from `id_token` for user-account ADC (`_decode_id_token_email`), and add best-effort STS introspection (`_introspect_principal`, POSTing to `credentials.token_info_url`) for WIF/WLIF credentials, falling back to the audience path if introspection fails or returns nothing usable. Render `principal` as a visible "Account: …" line in `AuthStatusBadge.tsx`, not only in a tooltip.
- [ ] 5.5 When a real Workforce Identity Federation pool is available (blocked on task group 1), confirm what `_introspect_principal`'s STS introspection call actually returns for a WIF-exchanged token, since Google does not publicly document the `/v1/introspect` response schema; adjust the field-name fallback order in `_introspect_principal` if the real response uses different keys than `email`/`username`/`sub`.
</content>
