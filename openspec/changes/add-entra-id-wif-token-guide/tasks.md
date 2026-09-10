## 1. Write the guide

- [x] 1.1 Create `docs/AUTHENTICATION.md` with a "Prerequisites (already done by your administrator)" section listing: workforce pool ID, workforce pool provider ID (mapped to Entra ID), workforce-pool user project, and IAM authorization of the reader's Entra ID identity against the pool (per "End-user token guide exists and is scoped to token acquisition only").
- [x] 1.2 Document the interactive path: generating/obtaining a login-config file, `gcloud auth login --login-config=<path>` and `gcloud auth application-default login --login-config=<path>`, and retrieving the token via `gcloud auth print-access-token` / `gcloud auth application-default print-access-token` (per "Guide documents interactive browser-based token acquisition").
- [x] 1.3 Document the headless path: obtaining an Entra ID OIDC ID token and exchanging it via a `curl` POST to `https://sts.googleapis.com/v1/token` with the token-exchange grant, `subject_token_type=urn:ietf:params:oauth:token-type:id_token`, the pool/provider audience, and `options.userProject`, including the expected JSON response shape (per "Guide documents headless token acquisition via the STS REST API").
- [x] 1.4 Add a worked example calling a Gemini Enterprise/Discovery Engine endpoint (e.g. list assistants or search) with the obtained token, showing both the `Authorization: Bearer <token>` and `X-Goog-User-Project` headers and explaining why the latter is required for a WIF principal (per "Guide includes a worked Gemini Enterprise API call using the obtained token").
- [x] 1.5 Rename the guide to `docs/AUTHENTICATION.md` (matching the repo's ALL-CAPS `docs/` convention) and add a "Cross-Application Access" section with a Mermaid sequence diagram showing a second app on the same Entra tenant reusing its own sign-in token, exchanging via a same-pool WIF provider with matching attribute mapping, and calling the Gemini Enterprise API — no second user-facing prompt (per "Guide documents seamless cross-application access on a shared Entra ID tenant").

## 2. Link from README

- [x] 2.1 Add one link line in README.md's Prerequisites section and Documentation list pointing to `docs/AUTHENTICATION.md`, described as end-user (and cross-application) Entra ID/WIF token acquisition, without editing the existing operator ADC instructions (per "Guide is discoverable from the README").

## 3. Review

- [x] 3.1 Re-read the finished guide end-to-end as a reader with only the stated prerequisites and confirm every command/request is copy-pasteable with placeholders clearly marked, and that no administrator/provisioning step leaked in.
</content>
<parameter name="i">Writing tasks.md for the new change