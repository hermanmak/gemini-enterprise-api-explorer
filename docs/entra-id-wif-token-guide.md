# Getting a Gemini Enterprise API token via Workforce Identity Federation (Microsoft Entra ID)

This guide is for an **end user** at a customer organization who wants to call the Gemini Enterprise (Discovery Engine) API directly — from a script, notebook, or their own client — using their existing Microsoft Entra ID corporate identity, authenticated through Google Cloud's Workforce Identity Federation (WIF).

It covers **only how to obtain and use the token**. It does not cover setting up Workforce Identity Federation itself.

## Prerequisites (already done by your administrator)

Before you can follow this guide, your GCP/IT administrator must have already:

1. Created a **workforce identity pool** and a **workforce identity pool provider** configured for Microsoft Entra ID (OIDC), in the same GCP organization as the project that runs Gemini Enterprise.
2. Granted your Entra ID identity (directly or via a group) the IAM roles needed to call the Gemini Enterprise API (e.g. Discovery Engine roles) on the target project, plus `roles/serviceusage.serviceUsageConsumer` (or an equivalent role containing `serviceusage.services.use`) on the **workforce-pool user project**.
3. Given you the following values (they're customer-specific — nothing below is a working default):
   - `WORKFORCE_POOL_ID` — the workforce identity pool ID
   - `WORKFORCE_PROVIDER_ID` — the workforce identity pool provider ID
   - `WORKFORCE_POOL_USER_PROJECT` — the project number/ID used for quota and billing of your WIF sign-ins
   - `PROJECT_NUMBER` — the project number of the GCP project running Gemini Enterprise (used later as the API's quota project; may be the same as `WORKFORCE_POOL_USER_PROJECT`)
   - `ENGINE_ID` / `LOCATION` — the Gemini Enterprise engine/app you're calling

If any of these don't exist yet, this guide isn't for you — ask your administrator to complete Google's [Workforce Identity Federation setup for Microsoft Entra ID](https://cloud.google.com/iam/docs/workforce-sign-in-microsoft-entra-id) first.

There are two ways to get a token: **interactively** (you have a browser) or **headlessly** (a script/service with no browser). Pick one.

## Option A: Interactive sign-in with the gcloud CLI

Use this if you're a person at a terminal.

1. [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install) if you don't already have it.

2. Get a **login configuration file** for your pool/provider. Your administrator may hand you this file directly, or you can generate it yourself if you have read access to the provider resource:

   ```bash
   gcloud iam workforce-pools create-login-config \
       locations/global/workforcePools/WORKFORCE_POOL_ID/providers/WORKFORCE_PROVIDER_ID \
       --output-file=login-config.json
   ```

   This file only contains public endpoint metadata (audience, auth URL, token URL) — no secrets.

3. Sign in. Two variants, depending on what you need the token for:

   - **For `gcloud`/`gsutil`/`bq` commands** and to get a token via `gcloud auth print-access-token`:

     ```bash
     gcloud auth login --login-config=login-config.json
     ```

   - **For a local script or app that reads Application Default Credentials (ADC)** — for example, calling the Gemini Enterprise API with a Google Cloud client library:

     ```bash
     gcloud auth application-default login --login-config=login-config.json
     ```

   Either command opens a browser, redirects you to sign in with your Microsoft Entra ID account, and on success stores credentials locally. gcloud transparently exchanges your Entra ID sign-in for a Google Cloud access token via Security Token Service — you don't do the token exchange yourself.

4. Retrieve the access token:

   ```bash
   # If you used `gcloud auth login`:
   gcloud auth print-access-token

   # If you used `gcloud auth application-default login`:
   gcloud auth application-default print-access-token
   ```

   Each command prints a short-lived Google Cloud access token (an OAuth `Bearer` token). When it expires, gcloud automatically re-exchanges your still-valid Entra ID session for a new one on the next `print-access-token` call — you don't need to sign in again until your Entra ID session itself expires.

5. Skip to [Calling the Gemini Enterprise API](#calling-the-gemini-enterprise-api).

## Option B: Headless token exchange (scripts/automation)

Use this if there's no browser available — for example, a CI job or scheduled script running under a service identity that authenticates to Entra ID directly (client-credentials flow, or whatever non-interactive Entra ID flow your administrator has configured for this purpose).

1. Obtain an **Entra ID–issued OIDC ID token** using whatever non-interactive method your administrator set up for automation (e.g. an Entra ID app registration's client-credentials or on-behalf-of flow). This is outside Google's scope — it's a standard Entra ID token acquisition, and the result is a JWT.

2. Exchange that ID token for a Google Cloud access token by calling Security Token Service directly:

   ```bash
   curl https://sts.googleapis.com/v1/token \
       --data-urlencode "audience=//iam.googleapis.com/locations/global/workforcePools/WORKFORCE_POOL_ID/providers/WORKFORCE_PROVIDER_ID" \
       --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
       --data-urlencode "requested_token_type=urn:ietf:params:oauth:token-type:access_token" \
       --data-urlencode "scope=https://www.googleapis.com/auth/cloud-platform" \
       --data-urlencode "subject_token_type=urn:ietf:params:oauth:token-type:id_token" \
       --data-urlencode "subject_token=ENTRA_ID_OIDC_TOKEN" \
       --data-urlencode "options={\"userProject\":\"WORKFORCE_POOL_USER_PROJECT\"}"
   ```

   Replace `ENTRA_ID_OIDC_TOKEN` with the JWT from step 1, and the other placeholders with the values from [Prerequisites](#prerequisites-already-done-by-your-administrator).

3. The response looks like:

   ```json
   {
     "access_token": "ya29.dr.AaT61Tc6Ntv1ktbGkaQ9U_MQfiQw...",
     "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ```

   `access_token` is your Google Cloud bearer token, valid for `expires_in` seconds (typically one hour). When it expires, repeat step 2 with a fresh Entra ID ID token from step 1.

## Calling the Gemini Enterprise API

Once you have an access token from either option above, call the Gemini Enterprise (Discovery Engine) API directly. Two headers are required:

- `Authorization: Bearer <access_token>`
- `X-Goog-User-Project: PROJECT_NUMBER` — **required explicitly.** A Workforce Identity Federation principal typically has no GCP project associated with its credentials (unlike a user or service-account identity), so the API call must specify the billing/quota project itself rather than relying on it being inferred from the token.

Example — listing assistants for an engine:

```bash
ACCESS_TOKEN="<token from Option A or B>"

curl -X GET \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "X-Goog-User-Project: PROJECT_NUMBER" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/PROJECT_NUMBER/locations/LOCATION/collections/default_collection/engines/ENGINE_ID/assistants"
```

Substitute `PROJECT_NUMBER`, `LOCATION`, and `ENGINE_ID` with the values from [Prerequisites](#prerequisites-already-done-by-your-administrator). Any other Gemini Enterprise/Discovery Engine REST endpoint your Entra ID identity is authorized for follows the same pattern — same two headers, different URL and body.

## Ending your session

- Interactive (`gcloud auth login`): `gcloud auth revoke` to sign out; `gcloud auth list` to see active sessions.
- Headless: simply stop requesting new Entra ID ID tokens; there is no persistent Google-side session to revoke beyond letting the last-issued access token expire.

## Further reading

- [Obtain short-lived tokens for Workforce Identity Federation](https://cloud.google.com/iam/docs/workforce-obtaining-short-lived-credentials) (Google's canonical reference for the commands and REST calls above)
- [Configure Workforce Identity Federation with Microsoft Entra ID](https://cloud.google.com/iam/docs/workforce-sign-in-microsoft-entra-id) (administrator setup — not needed if your admin has already done this)
</content>
<parameter name="i">Writing the end-user Entra ID WIF token acquisition guide