## Purpose

Requirements that the backend's ADC-based Google Cloud authentication (used by every `api-explorer` route and by `SearchClient`) functions correctly — token acquisition, refresh, and quota-project resolution — when the active credential is a Workforce Identity Federation `external_account` identity, plus a way to observe which identity kind and account are actually active in the UI.

## Requirements

### Requirement: Google Cloud API calls succeed with a WIF identity
Every backend call site that sources credentials from `google.auth.default()` — the `api-explorer` routes (`get_engine_details`, `web_grounding_search`, `get_engine_data_stores`, `list_assistants`, `list_agents`, `get_agent`, `stream_assist`, and the `deep-research` plan/run flow which calls `stream_assist`) and `SearchClient`'s `discoveryengine.SearchServiceClient` — SHALL complete successfully when the ADC principal resolved by `default()` is a Workforce Identity Federation `external_account` identity, with no code path that assumes the principal is a user or service-account credential.

#### Scenario: WIF principal lists agents
- **WHEN** ADC is configured against a Workforce Identity Federation credential config and a client calls `GET /api-explorer/list-agents/{engine_id}`
- **THEN** the backend obtains a valid bearer token from the WIF-sourced credentials and returns the agent list exactly as it would for a user-ADC or service-account-ADC principal

#### Scenario: WIF principal runs a search
- **WHEN** ADC is configured against a Workforce Identity Federation credential config and a client triggers a search through `SearchClient.search`
- **THEN** the `discoveryengine.SearchServiceClient` authenticates the request using the WIF-sourced credentials and returns results identically to a non-WIF ADC principal

### Requirement: Expired WIF credentials are refreshed before use
For every route that checks `credentials.valid` before issuing a request, an invalid or expired WIF-sourced credential SHALL be refreshed via `credentials.refresh(AuthRequest())` before the request is sent, using the same generic refresh call already used for other ADC credential types.

#### Scenario: Expired WIF token is refreshed
- **WHEN** a route's `default()` call returns a WIF `external_account` credential whose `.valid` is `False`
- **THEN** the route calls `credentials.refresh(AuthRequest())` and uses the resulting `credentials.token` in the `Authorization` header, without raising or short-circuiting due to the credential's type

### Requirement: Quota-project resolution tolerates a WIF principal with no ADC project
When `use_adc_quota` is `True` and the ADC-resolved project (`adc_project` from `default()`) is empty — the common case for a Workforce Identity Federation principal that has no associated GCP project — the system SHALL fall back to the caller-supplied `project_number` for the `X-Goog-User-Project` header instead of sending an empty or `None` value.

#### Scenario: WIF ADC reports no project
- **WHEN** `use_adc_quota` is `True`, the resolved credentials are a WIF `external_account` identity, and `default()` returns an empty `adc_project`
- **THEN** the route sets `X-Goog-User-Project` to the request's `project_number` rather than an empty or `None` value

#### Scenario: WIF ADC has an explicit quota project configured
- **WHEN** `use_adc_quota` is `True` and the WIF credential config sets `quota_project_id`, so `default()` returns a non-empty `adc_project`
- **THEN** the route uses that `adc_project` for `X-Goog-User-Project`, matching existing behavior for non-WIF ADC

### Requirement: WIF-based ADC setup is documented
The project README SHALL document how to configure Application Default Credentials against a Workforce Identity Federation credential config (e.g. `gcloud auth application-default login --login-config=<config>` or `GOOGLE_APPLICATION_CREDENTIALS` pointed at the WIF credential-config JSON) as a supported alternative to the existing user-ADC setup instructions.

#### Scenario: Operator sets up WIF-based ADC
- **WHEN** an operator follows the README to configure ADC using a Workforce Identity Federation credential config instead of `gcloud auth application-default login`
- **THEN** the documented steps result in a working ADC principal that the backend can use for every API-explorer route without further code changes

### Requirement: Active authentication identity is visible in the UI
The system SHALL expose a read-only backend endpoint that introspects the Application Default Credentials currently in effect and classifies the resolved principal's kind (Workforce Identity Federation, Workload Identity Federation, service account, user account, attached service account, or impersonated), and the UI SHALL display that classification so a user can confirm which identity type — including WIF — the backend is actually using, without requiring the UI to collect or transmit any credential material itself.

#### Scenario: Backend is authenticated via Workforce Identity Federation
- **WHEN** the backend's ADC resolves to a Workforce Identity Federation credential (either the browser sign-in flow or a file/URL/executable-sourced workforce credential config) and a client requests the auth-status endpoint
- **THEN** the response identifies the credential kind as Workforce Identity Federation and the UI renders that label, distinguishing it from service-account or user-account ADC

#### Scenario: Backend is authenticated via non-WIF ADC
- **WHEN** the backend's ADC resolves to a user account, service account key, attached service account, or impersonated credential
- **THEN** the response identifies the corresponding non-WIF credential kind and the UI renders that label instead of claiming WIF is active

#### Scenario: ADC cannot be resolved
- **WHEN** the backend has no usable Application Default Credentials configured
- **THEN** the endpoint returns a failure result with the underlying error rather than crashing, and the UI shows an explicit "authentication not configured" state instead of a stale or blank badge

### Requirement: The active account identity is displayed, not just the credential kind
In addition to the credential kind, the system SHALL surface the specific account behind it wherever one is resolvable — the signed-in user's email for user-account ADC, the service account email for service-account/attached-service-account/impersonated credentials, and a best-effort account or subject identifier for Workforce/Workload Identity Federation credentials — and the UI SHALL render it as a visible field, not only as a hover tooltip. Where no identifier can be resolved, the system SHALL omit the field rather than display a placeholder or fabricated value.

#### Scenario: User-account ADC exposes the signed-in email
- **WHEN** the backend's ADC resolves to a user-account credential carrying an OIDC ID token with an `email` claim
- **THEN** the auth-status response's principal is that email address and the UI displays it as a visible "Account: …" line

#### Scenario: Service-account-family credentials expose the service account email
- **WHEN** the backend's ADC resolves to a service-account key, an attached (metadata-server) service account, or an impersonated credential
- **THEN** the auth-status response's principal is the relevant service account email and the UI displays it as a visible line

#### Scenario: WIF principal resolution degrades gracefully
- **WHEN** the backend's ADC resolves to a Workforce or Workload Identity Federation credential and best-effort STS introspection of the access token does not yield a usable account identifier (Google does not publicly document the introspection response schema)
- **THEN** the system falls back to the credential's pool/provider audience path as the displayed identifier rather than failing the whole auth-status request or showing nothing
</content>
