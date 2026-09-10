## ADDED Requirements

### Requirement: End-user token guide exists and is scoped to token acquisition only
The repository SHALL contain a standalone documentation file, `docs/entra-id-wif-token-guide.md`, aimed at an end user (not this app's operator) who wants to obtain a Google Cloud access token via an already-configured Workforce Identity Federation (WIF) pool and provider federated with Microsoft Entra ID, in order to call the Gemini Enterprise API. The guide SHALL open with a "Prerequisites" section listing exactly what an administrator must already have configured — a workforce pool, a workforce pool provider mapped to Entra ID, a workforce-pool user project, and the reader's Entra ID account authorized against the pool — and SHALL NOT include steps for creating or configuring the pool, provider, Entra ID app registration, or IAM bindings.

#### Scenario: Reader with prerequisites in place can follow the guide standalone
- **WHEN** an end user whose administrator has already configured a WIF pool/provider for Entra ID reads `docs/entra-id-wif-token-guide.md`
- **THEN** the document's Prerequisites section lets them confirm every precondition is met before proceeding, and no later step requires provisioning or administrator-level GCP IAM actions

#### Scenario: Guide does not duplicate administrator setup content
- **WHEN** a reader looks for pool/provider/app-registration creation steps in `docs/entra-id-wif-token-guide.md`
- **THEN** those steps are absent, and the document instead states they are an administrator prerequisite performed once, out of band

### Requirement: Guide documents interactive browser-based token acquisition
The guide SHALL describe the interactive path for a human end user: obtaining a workforce pool login-config file, running `gcloud auth login --login-config=<path>` (or `gcloud auth application-default login --login-config=<path>` when the token is needed as Application Default Credentials for a local script) to sign in through a browser redirect to Microsoft Entra ID, and retrieving the resulting access token via `gcloud auth print-access-token` (or `gcloud auth application-default print-access-token` for the ADC variant).

#### Scenario: End user obtains a token interactively
- **WHEN** an end user follows the interactive section of the guide with a valid Entra ID account authorized against the workforce pool
- **THEN** the documented `gcloud` commands, executed in order, result in a working Google Cloud access token retrievable via `gcloud auth print-access-token` without any manual STS request

### Requirement: Guide documents headless token acquisition via the STS REST API
The guide SHALL describe the non-interactive path for scripts/automation: obtaining an Entra ID–issued OIDC ID token through the customer's chosen Entra ID token-acquisition method, then exchanging it for a Google Cloud access token by POSTing to `https://sts.googleapis.com/v1/token` with `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`, `subject_token_type=urn:ietf:params:oauth:token-type:id_token`, the pool/provider `audience`, and the workforce-pool user project as `options.userProject`.

#### Scenario: Automation obtains a token without gcloud
- **WHEN** a script holds a valid Entra ID OIDC ID token for a principal authorized against the workforce pool and issues the documented STS REST request with that token as `subject_token`
- **THEN** the response contains a Google Cloud `access_token` usable as a bearer token, matching the request/response shapes shown in the guide

### Requirement: Guide includes a worked Gemini Enterprise API call using the obtained token
The guide SHALL include at least one worked example that uses the access token obtained via either documented path to call a Gemini Enterprise/Discovery Engine API endpoint directly (e.g. an `assistants` list or `search` call), and SHALL note that the `X-Goog-User-Project` header must be set explicitly to a billing/quota project number, since a WIF principal's resolved credentials typically carry no associated GCP project.

#### Scenario: Reader calls the Gemini Enterprise API with the obtained token
- **WHEN** an end user follows the worked example, substituting their own project number, engine ID, and access token obtained from either the interactive or headless path
- **THEN** the example request includes an `Authorization: Bearer <token>` header and an explicit `X-Goog-User-Project` header, and does not omit or leave the quota-project header as a placeholder with no explanation

### Requirement: Guide is discoverable from the README
The README's Prerequisites section SHALL link to `docs/entra-id-wif-token-guide.md` so a reader evaluating Entra ID/WIF access to the Gemini Enterprise API can find it, without altering the README's existing operator-focused ADC setup instructions.

#### Scenario: Reader discovers the guide from the README
- **WHEN** a reader reviews the README's Prerequisites section
- **THEN** they find a link to `docs/entra-id-wif-token-guide.md` described as covering end-user token acquisition via Entra ID/WIF, distinct from the operator ADC setup steps already documented there
</content>
<parameter name="i">Writing spec delta for new entra-id-wif-token-guide capability