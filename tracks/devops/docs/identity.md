# Optional identity study with a personal Auth0 tenant

The core labs require no identity provider or account. You can learn the flow on paper. If you want a live experiment, use your own personal sandbox and synthetic users only; this does not grant access to any company system.

Auth0's [pricing page](https://auth0.com/pricing) advertised a Free plan and no credit card needed to sign up when checked on 2026-10-30. Features, quotas, and trial behavior can change. Check the plan and limits displayed during signup, skip paid features, and stop if a payment method or upgrade is required. There is no need to create a custom domain, paid connection, or organization integration for this exercise.

## Read the boundary first

| Item | Intended purpose | Handling |
| --- | --- | --- |
| Client ID | Identify an application registration | Usually public; it is not a password |
| Client secret | Authenticate a confidential application | Server side only; never in a browser bundle or Git |
| ID token | Describe authentication to the client | Do not substitute it for an API access token |
| Access token | Authorize a request to an intended API | Validate intended audience, issuer, signature, lifetime, and required permissions |
| Session cookie | Maintain a web application's session | Use appropriate secure, HttpOnly, SameSite, and expiration settings |
| Refresh token | Obtain new tokens subject to policy | Sensitive credential; avoid collecting it in notes or screenshots |

OIDC adds an identity layer to OAuth 2.0. Logging in answers who authenticated. Application authorization still decides which operation that identity may perform. An authenticated user must not gain access merely by guessing another record's identifier.

## Walkthrough

1. Read the [Auth0 quickstart catalog](https://auth0.com/docs/quickstarts). Select a maintained local sample for the application type you want to understand. A browser SPA and a server-rendered confidential web app require different registrations and secret handling.
2. Create a personal sandbox tenant and one application only if you choose the live path. Use a distinct name such as `personal-identity-lab`. Avoid inviting anyone or connecting a company domain.
3. Follow that sample's documented callback, logout, and web-origin settings exactly, including scheme, host, port, and path. Use localhost where the sample supports it. Do not use wildcard callbacks as a workaround for a mismatch.
4. Put sample configuration in an ignored local file following the sample's instructions. Keep the client secret out of browser-visible variables. Use a synthetic local record and a personal test identity; no company records or credentials belong in the sample.
5. If the sample calls an API, register a separate toy API identifier and a narrow permission such as `notes:read`. Request the intended audience. Use the SDK's recommended Authorization Code flow; public clients use [PKCE](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-pkce) instead of pretending they can keep a client secret.
6. Inspect the sequence in browser developer tools without saving token-bearing URLs or headers. Find the redirect to login, callback, and authenticated API request. Do not paste live tokens into hosted decoders or documents.
7. Verify success and failure: no token, expired/invalid token, wrong audience, and insufficient permission should not grant access. Use the sample's supported tests or a local validation harness. Decoding a JWT payload alone does not verify it. The API must follow [access token validation](https://auth0.com/docs/secure/tokens/access-tokens/validate-access-tokens).
8. Log out, remove the toy user/application/API when finished, and delete local secret files. Revoke any credentials that were exposed; deleting a file does not revoke a credential. Tenant deletion is optional if you want to retain your own sandbox.

## Paper alternative

Draw browser → application → identity provider → callback → application → API. Label where `state`, PKCE, issuer/audience validation, session expiration, and record ownership checks apply. Predict the difference between a wrong callback configuration, rejected token, missing permission, and an unavailable API. This exercise needs no signup, keys, or public endpoint.
