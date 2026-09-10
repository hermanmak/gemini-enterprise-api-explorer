## Context

Today the repo's only authentication documentation is in `README.md` and describes the *operator's* ADC setup for running this app's own backend (`gcloud auth application-default login`, optionally against a WIF login-config per the `wif-authentication` spec). That is a different audience and a different token than what this change targets: an *end user* at a customer organization who wants to obtain a Google Cloud OAuth access token themselves — for a script, notebook, or their own client — to call the Gemini Enterprise (Discovery Engine) REST API directly, authenticating with their existing Microsoft Entra ID corporate identity via Workforce Identity Federation (WIF).

Google Cloud's WIF flow for an already-provisioned pool/provider has two shapes documented by Google (`Obtain short-lived tokens for Workforce Identity Federation`):
1. **Browser-based interactive sign-in**: `gcloud auth login --login-config=<login-config.json>` (or `gcloud auth application-default login --login-config=...` for app-consumable ADC), which redirects the user's browser to the configured IdP — Entra ID in this case — and transparently exchanges the resulting OIDC ID token for a Google Cloud access token via Security Token Service (STS).
2. **Headless / non-interactive**: obtain an Entra ID–issued OIDC ID token directly (e.g. via an Entra ID app registration configured for the resource owner or client-credentials-style flow appropriate to the customer's automation), then POST it to `https://sts.googleapis.com/v1/token` (token-exchange grant) to receive a short-lived Google Cloud access token, without any `gcloud` dependency.

Both shapes assume a workforce pool + provider already exist, mapped to Entra ID as the OIDC IdP, in the same GCP organization as the project running Gemini Enterprise, and that the end user's Entra ID identity is already authorized against that pool (IAM binding + `serviceusage.services.use` on the workforce-pool user project). Provisioning that pool/provider/app-registration is administrator work covered by Google's own setup guides, not by this change.

## Goals / Non-Goals

**Goals:**
- Give an end user a single, accurate, copy-pasteable procedure to go from "I have an Entra ID account and someone told me WIF is set up" to "I have a bearer token I can put in an `Authorization` header for the Gemini Enterprise API."
- Cover both the interactive (gcloud/ADC) and headless (raw STS REST exchange) paths, since customers automating against the API from a service/script cannot use a browser-based flow.
- Show one worked example calling a real Gemini Enterprise/Discovery Engine endpoint (e.g. `listAssistants` or `search`) with the obtained token, including the `X-Goog-User-Project` header this app's own `wif-authentication` spec already established is required when the WIF principal has no ADC-resolved project.
- State every prerequisite explicitly (workforce pool ID, provider ID, workforce-pool user project, IAM role) as placeholders the end user fills in from values their admin gives them, so the guide is self-contained without requiring the reader to also read Google's admin-setup docs to understand what those placeholders mean.

**Non-Goals:**
- Creating or configuring the workforce pool, provider, Entra ID app registration, attribute mapping, or IAM bindings — that is administrator setup, assumed already done, and out of scope per the proposal.
- Modifying this app's backend/frontend or the existing `wif-authentication` spec — this is a standalone reference document for a different audience (external end users, not this app's own ADC-based server process).
- Documenting SAML-based Entra ID federation — Entra ID supports both OIDC and SAML for WIF; the guide covers OIDC only since it is the simpler and more commonly recommended path for new Entra ID WIF setups and keeps the headless REST example concrete (one subject-token type).

## Decisions

- **New standalone file under `docs/`, not a README section.** The README is operator-focused (running this app); mixing in an end-user, different-audience, multi-path credential guide would bloat it. A linked file keeps each document single-purpose. Alternative considered: extend the README's existing ADC section — rejected, wrong audience and would make the README's setup instructions harder to follow.
- **Document both interactive and headless paths, not just one.** An end user testing manually and a customer automating a script have different needs; Google documents both as first-class options for an already-provisioned pool, and omitting either would make the guide incomplete for half its audience.
- **OIDC only, not SAML.** Keeps the guide concrete and matches the most common new-setup recommendation; a future change can add a SAML variant if a customer needs it (documented as a known gap, not silently unsupported).
- **Treat the workforce pool ID / provider ID / user-project as reader-supplied placeholders, not invented example values presented as real.** The guide clearly labels them as values the reader's GCP administrator provides, consistent with Google's own placeholder convention (`WORKFORCE_POOL_ID`, etc.), so nothing in the doc could be mistaken for a working default.
- **Include the `X-Goog-User-Project` / quota-project note from the existing `wif-authentication` spec.** WIF principals typically resolve no ADC project, and Gemini Enterprise API calls need an explicit quota project; omitting this would produce a guide that "works" up to the first `403`/quota error.
- **Guide the file as `docs/AUTHENTICATION.md`, not `docs/entra-id-wif-token-guide.md`.** Matches the repo's existing ALL-CAPS `docs/` naming convention (`docs/NOTEBOOKLM.md`, `docs/ARCHITECTURE.md`) and better reflects the file's broadened scope after adding cross-application coverage. Alternative considered: keep the original descriptive filename — rejected once the guide stopped being purely about one token-acquisition flow and started covering an authentication topic broadly (single-app and cross-app).
- **Document cross-application access as "add a second WIF provider to the same pool with matching attribute mapping," not Entra ID On-Behalf-Of token exchange, as the primary path.** The requesting scenario (a second app, e.g. ARIA, on the *same* Entra tenant, with access already assumed grantable) is exactly the case Google's own workforce-pool model handles with zero extra runtime hops: one more provider, same pool, same `google.subject` mapping, so the same human is the same Google principal through either app's login. OBO token exchange (Entra-side) is documented as a one-paragraph fallback for when the calling app can't get its own provider added (different admin domain), not as the primary flow, to keep the common case simple.

## Risks / Trade-offs

- [Google's STS/credential-config surface can change] → The guide links to Google's canonical WIF docs for the always-current reference and only reproduces the specific commands/requests needed for this app's use case, reducing (not eliminating) drift risk.
- [No live Entra ID + WIF pool available in this environment to execute the flow end-to-end] → Every command and REST call is taken verbatim from Google's official Workforce Identity Federation documentation rather than invented; the worked API example reuses this app's own already-validated `X-Goog-User-Project`/header pattern from `wif-authentication`.
- [Guide could be mistaken for admin setup instructions] → The guide opens with an explicit "Prerequisites (already done by your administrator)" section listing exactly what must exist before following the steps, so a reader without those prerequisites is redirected rather than stuck mid-procedure.
</content>
<parameter name="i">Writing design.md for the new change