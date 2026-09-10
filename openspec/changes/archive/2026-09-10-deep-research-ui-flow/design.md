## Context

This app (`backend/api/routes/api_explorer.py` + `frontend/components/ApiExplorer.tsx`) is a single-shot REST explorer: pick an engine/assistant/agent, fire one request, render one response blob. It talks to Discovery Engine with ADC, no server-side session persistence — `session_id` is just a text field the user copies between calls.

Live testing against `hmak-search-engine-genai` (project `812896915478`) established the actual `deep_research` contract, which this explorer's existing `stream_assist` route cannot satisfy:

- `deep_research`'s `agentInvocationSpec` has no `invocationMode: AUTOMATIC` (unlike every other agent in the catalog) and its definition is `managedAgentDefinition.researchAssistantAgentConfig` — a collaborative, plan-then-run contract, not a direct tool call.
- Calling it on v1 GA with the minimal `agentsSpec`-only payload the existing route sends returns `500 INTERNAL` immediately (verified once; see Risks).
- The working contract is v1alpha with `assist_skipping_mode: request_assist`, `answer_generation_mode: agent`, `agents_config`, `agents_spec`, and `tools_spec: {vertex_ai_search_spec, web_grounding_spec}`.
- Turn 1 (the user's real question) returns a `RESEARCH_PLAN` chunk and mints a session; turn 2 (literal query `"Start research"`, same session) streams the run: repeated `RESEARCH_QUESTION`/`RESEARCH_ANSWER` pairs, a `RESEARCH_REPORT` with `textGroundingMetadata` citations, a `RESEARCH_AUDIO_SUMMARY` (a `{mimeType, fileId}` pointer, not inline audio), and a terminal `state: SUCCEEDED` echo chunk. The full run took ~8 minutes over one held-open HTTP connection.
- The engine's agent catalog also contains A2A-wrapped agents (`a2aAgentDefinition`, e.g. "Antigravity Agent", "Beauty") which this app has never invoked and are out of scope for this change and the standard flow alike.

## Goals / Non-Goals

**Goals:**
- Drive `deep_research` end-to-end from the UI: submit a question, see the plan, confirm, watch the run progress, read the final report with citations.
- Do this without touching the existing `stream_assist` route or its request/response contract — every other agent keeps working exactly as today.
- Make the "which agents can I actually run from this UI" boundary explicit and visible, not a 500 the user has to debug.

**Non-Goals:**
- No generic multi-turn orchestration framework for arbitrary agents — this is a `deep_research`-specific code path.
- No A2A agent invocation support (explicit product decision, not a technical limitation being worked around).
- No durable/cross-restart session persistence — this is a dev/demo explorer; in-memory-on-the-client session handoff is sufficient, matching how `session_id` already works for the standard flow.
- No resolution of the `RESEARCH_AUDIO_SUMMARY` binary in this change — the endpoint that serves it hasn't been identified; ship the plan/run/report path and surface the raw `fileId` rather than block on it.
- No attempt to determine the minimal required subset of the three v1alpha envelope fields — ship with the proven-working full envelope from the reference contract; trimming it is a separate follow-up if ever needed.

## Decisions

**1. Two new, dedicated backend routes, not an extension of `stream_assist`.**
`POST /api-explorer/deep-research/plan` (turn 1: real query + full v1alpha envelope, returns the plan text + minted `session_id`) and `POST /api-explorer/deep-research/run` (turn 2: given a `session_id`, sends `"Start research"` and proxies the run). Alternative considered: add an `is_deep_research` branch inside `stream_assist`. Rejected — the payload shape, API version (v1alpha vs v1), and response handling are different enough that branching would make the generic route harder to reason about and risk regressing it. Keeping them fully separate matches the proposal's "keep all others the standard interaction flow" constraint literally: zero shared code path, zero regression surface.

**2. Session handoff stays client-held, not server-stored.**
The frontend receives `session_id` from `/plan` and passes it explicitly to `/run`, the same pattern the standard flow already uses. Alternative: server-side session store (dict or DB) keyed by browser session. Rejected for this change — no other part of this app has server-side state, and adding it here for one agent is disproportionate. Trade-off: a page refresh between plan and run loses the handoff; acceptable for an explorer tool (documented in Risks).

**3. Proxy the run as a stream (SSE) from `/run`, not buffer-then-return.**
`stream_assist` today buffers the whole upstream response with `requests.post()` then returns one JSON blob — fine for sub-second calls, wrong for an 8-minute run: the browser would show nothing for 8 minutes with no way to distinguish "working" from "hung." `/run` reads the upstream response incrementally and forwards each parsed chunk to the client as it arrives (SSE), so the UI can render each `RESEARCH_QUESTION`/`RESEARCH_ANSWER` as it lands. Alternative considered: fire-and-forget the upstream call server-side, return a job ID, have the frontend poll a status endpoint. Rejected — needs a results store and introduces polling-interval latency for no real benefit at this app's single-user, single-process scale; SSE over one already-open request is simpler and matches this app's stateless-backend pattern.

**4. Agent-picker gating by definition-kind allowlist, enforced in the UI, not `list-agents`.**
`list-agents` keeps returning every agent unfiltered (it's a diagnostic passthrough — hiding data there would make it a worse debugging tool). The picker that lets a user *start an interactive turn* filters to an allowlist: `workflowAgentDefinition` and `lowCodeAgentDefinition` (no-code) plus the `deep_research` agent (`managedAgentDefinition.researchAssistantAgentConfig`, routed to the new flow instead of `stream_assist`). Everything else — currently only `a2aAgentDefinition` — is shown greyed out with an explicit "not supported" label instead of silently disappearing, so the boundary is visible rather than a mystery 500. Denylisting only `a2a` was considered and rejected: it fails open for any future agent-definition kind Google adds, silently offering broken agents. Allowlisting fails closed instead.

## Risks / Trade-offs

- [Risk] The "missing envelope → `500`" behavior was reproduced once, not confirmed deterministic; Google's own error text ("try again") is boilerplate for transient errors. → Mitigation: `/plan` and `/run` always send the full envelope (Decision 4/Non-Goal), so this risk only matters if it turns out the 500 was unrelated noise — worth one more repeat call before this ships, tracked as a task.
- [Risk] Discovery Engine's `streamAssist` response is a top-level JSON array; it's not yet confirmed the HTTP transport actually delivers bytes incrementally (vs. buffering server-side and sending it all at once at minute 8 regardless of client-side streaming code). → Mitigation: verify with a raw chunked read during implementation; if the upstream doesn't stream, ship an honest "running, ~8 min typical" progress state instead of fake incremental rendering — don't simulate progress that isn't real.
- [Risk] An 8-minute single HTTP connection is fragile behind any reverse proxy or load balancer with a shorter idle timeout. → Mitigation: not applicable to this repo's current setup (direct `uvicorn`, no documented proxy in front); flagged as a known constraint if this app is ever deployed behind one.
- [Risk] Client-held session state means a page refresh mid-plan or mid-run loses the ability to resume. → Mitigation: accepted for an explorer tool; document as a known limitation in the UI copy, not silently swallowed.
- [Risk] `adkAgentDefinition` agents (e.g. "Glow & Go Analytics Platform") are neither explicitly supported ("no-code agents and deep research") nor explicitly excluded ("A2A") per the current product direction. → Mitigation: default them to unsupported/greyed-out alongside A2A until confirmed otherwise (see Open Questions) — safer to under-expose than to offer a path nobody has verified.

## Migration Plan

Purely additive: new routes, new frontend view, new picker filter. No schema, dependency, or existing-route changes. Deploy as a normal commit; no feature flag needed since nothing existing is touched. Rollback is deleting the new routes/components if `deep_research` behavior regresses — the standard flow is unaffected either way.

## Open Questions

- Is the `500` on a missing envelope deterministic, or could it have been a transient blip coincident with the malformed request? (one repeat call would settle this)
- Does the upstream `streamAssist` HTTP response actually deliver bytes progressively, or buffer server-side for the full ~8 minutes regardless? Determines whether the SSE proxy shows real progress or just an early "plan received" tick followed by a long gap.
- What endpoint resolves a `RESEARCH_AUDIO_SUMMARY` `fileId` into playable audio? Unidentified; needs a spike.
- Should `adkAgentDefinition` agents count as "no-code" (supported) or stay excluded alongside A2A? Defaulting to excluded pending a product decision.
- Is a plan-revision turn (user asks for changes instead of "Start research") in scope for this change, or is straight-through plan→run the only supported v1 path? Design above assumes straight-through only; revision would need a third route/state.
