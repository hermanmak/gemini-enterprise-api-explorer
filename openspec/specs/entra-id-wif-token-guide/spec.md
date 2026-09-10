## Purpose

Requirements for a standalone, end-user/automation-facing documentation guide (`docs/AUTHENTICATION.md`) that describes — entirely headlessly, with no `gcloud` CLI or browser required — how to obtain a Google Cloud access token through Workforce Identity Federation (WIF) with Microsoft Entra ID as the identity provider, sufficient to call the Gemini Enterprise API directly, assuming WIF is already provisioned by an administrator.

## Requirements

### Requirement: End-user token guide exists and is scoped to token acquisition only
The repository SHALL contain a standalone documentation file, `docs/AUTHENTICATION.md`, aimed at an end user or automation (not this app's operator) who wants to obtain a Google Cloud access token via an already-configured Workforce Identity Federation (WIF) pool and provider federated with Microsoft Entra ID, in order to call the Gemini Enterprise API, entirely headlessly (no `gcloud` CLI or browser required). The guide SHALL open with a "Prerequisites" section listing exactly what an administrator must already have configured — a workforce pool, a workforce pool provider mapped to Entra ID, a workforce-pool user project, and the reader's Entra ID account authorized against the pool — and SHALL NOT include steps for creating or configuring the pool, provider, Entra ID app registration, or IAM bindings.

#### Scenario: Reader with prerequisites in place can follow the guide standalone
- **WHEN** an end user whose administrator has already configured a WIF pool/provider for Entra ID reads `docs/AUTHENTICATION.md`
- **THEN** the document's Prerequisites section lets them confirm every precondition is met before proceeding, and no later step requires provisioning or administrator-level GCP IAM actions

#### Scenario: Guide does not duplicate administrator setup content
- **WHEN** a reader looks for pool/provider/app-registration creation steps in `docs/AUTHENTICATION.md`
- **THEN** those steps are absent, and the document instead states they are an administrator prerequisite performed once, out of band

### Requirement: Guide documents headless token acquisition via the STS REST API
The guide SHALL describe the non-interactive path for scripts/automation: obtaining an Entra ID–issued OIDC ID token through the customer's chosen Entra ID token-acquisition method, then exchanging it for a Google Cloud access token by POSTing to `https://sts.googleapis.com/v1/token` with `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`, `subject_token_type=urn:ietf:params:oauth:token-type:id_token`, the pool/provider `audience`, and the workforce-pool user project as `options.userProject`.

#### Scenario: Automation obtains a token without gcloud
- **WHEN** a script holds a valid Entra ID OIDC ID token for a principal authorized against the workforce pool and issues the documented STS REST request with that token as `subject_token`
- **THEN** the response contains a Google Cloud `access_token` usable as a bearer token, matching the request/response shapes shown in the guide

### Requirement: Guide includes a worked Gemini Enterprise API call using the obtained token
The guide SHALL include at least one worked example that uses the access token obtained via the STS token exchange to call a Gemini Enterprise/Discovery Engine API endpoint directly (e.g. an `assistants` list or `search` call), and SHALL note that the `X-Goog-User-Project` header must be set explicitly to a billing/quota project number, since a WIF principal's resolved credentials typically carry no associated GCP project.

#### Scenario: Reader calls the Gemini Enterprise API with the obtained token
- **WHEN** an end user follows the worked example, substituting their own project number, engine ID, and access token obtained from the STS token exchange
- **THEN** the example request includes an `Authorization: Bearer <token>` header and an explicit `X-Goog-User-Project` header, and does not omit or leave the quota-project header as a placeholder with no explanation

### Requirement: Guide documents seamless cross-application access on a shared Entra ID tenant
The guide SHALL include a section covering how a second application (federated through the same Microsoft Entra ID tenant) can obtain an authenticated user's Gemini Enterprise data via the API without prompting the user for a second sign-in, including a sequence diagram showing the calling application's backend, Entra ID, Google STS, and the Gemini Enterprise API, and stating that IAM access carries over automatically when the calling application's own workforce pool provider shares the same pool and attribute mapping as the one used for direct end-user access.

#### Scenario: Reader designs cross-application access
- **WHEN** an end user or integrator reads the cross-application section of `docs/AUTHENTICATION.md` to understand how a second app on the same Entra tenant can fetch a signed-in user's Gemini Enterprise data
- **THEN** the section's diagram and text show the calling application reusing its own Entra ID sign-in token to obtain a Google Cloud access token via STS with no additional user-facing prompt, and state the same-pool/same-attribute-mapping precondition required for existing IAM grants to carry over

### Requirement: Guide is discoverable from the README
The README's Prerequisites section SHALL link to `docs/AUTHENTICATION.md` so a reader evaluating Entra ID/WIF access to the Gemini Enterprise API can find it, without altering the README's existing operator-focused ADC setup instructions.

#### Scenario: Reader discovers the guide from the README
- **WHEN** a reader reviews the README's Prerequisites section
- **THEN** they find a link to `docs/AUTHENTICATION.md` described as covering end-user token acquisition via Entra ID/WIF (including cross-application access on a shared Entra tenant), distinct from the operator ADC setup steps already documented there
</content>
<parameter name="i">Creating main spec for the new entra-id-wif-token-guide capability