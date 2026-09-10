## Why

This app's own README only documents *operator*-side ADC setup (`gcloud auth application-default login`, optionally against a WIF login-config) for whoever runs the backend. It says nothing about how an *end user* at a customer that federates through Microsoft Entra ID obtains a Google Cloud token to call the Gemini Enterprise (Discovery Engine) API themselves — e.g. from a script, a notebook, or their own client calling the API directly rather than through this demo's backend. Customers evaluating Gemini Enterprise via Workforce Identity Federation (WIF) need a self-contained, end-user-facing procedure for this, assuming their GCP org's WIF pool/provider is already configured against Entra ID.

## What Changes

- Add a new standalone documentation file, `docs/AUTHENTICATION.md`, that describes only the end-user/automation steps to obtain a short-lived Google Cloud access token via an already-configured Workforce Identity Federation pool/provider federated with Microsoft Entra ID, for the purpose of calling the Gemini Enterprise API — entirely headlessly, assuming no `gcloud` CLI or browser is available.
- Cover the headless flow: obtaining an Entra ID–issued OIDC ID token, then exchanging it for a Google Cloud access token via the Security Token Service REST endpoint, plus a worked example calling a Gemini Enterprise/Discovery Engine endpoint with the resulting token.
- Add a "Cross-Application Access" section with a sequence diagram covering the case where a second application on the **same Microsoft Entra ID tenant** (e.g. an internal portal) wants to seamlessly fetch a signed-in user's Gemini Enterprise data via the API, with no second sign-in prompt — by giving the calling application its own workforce pool provider (same pool, same attribute mapping) so existing IAM access carries over.
- Explicitly out of scope: provisioning or configuring the workforce pool, provider, or Entra ID app registration — the guide assumes an administrator has already set these up in the same GCP organization as the project running Gemini Enterprise, and that the end user's Entra ID account is already authorized against the pool.
- Add a single link to the new guide from the README's Prerequisites section so it's discoverable, without altering the README's existing operator-focused ADC instructions.

## Capabilities

### New Capabilities
- `entra-id-wif-token-guide`: A documentation-only capability requiring that the repository contain an accurate, self-contained guide (`docs/AUTHENTICATION.md`) for an end user — or a second application on the same Entra tenant — to obtain a Google Cloud access token through Workforce Identity Federation with Microsoft Entra ID as the identity provider, sufficient to call the Gemini Enterprise API directly, assuming WIF is already provisioned.

### Modified Capabilities
(none — the existing `wif-authentication` spec covers this app's own backend ADC handling of WIF credentials generically; it does not cover an end-user-facing, Entra-ID-specific token-acquisition guide)

## Impact

- New file: `docs/AUTHENTICATION.md`.
- `README.md`: one new link line in the Prerequisites section pointing to the guide.
- No backend or frontend code changes; no new endpoints or UI.
</content>
<parameter name="i">Writing proposal.md for the new change