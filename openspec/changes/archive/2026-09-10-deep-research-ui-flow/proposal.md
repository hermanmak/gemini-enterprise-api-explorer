## Why

The `deep_research` agent on the Assist endpoint (`assistants/default_assistant:streamAssist`) does not follow the single-shot request/response contract every other agent in this app uses. It requires a v1alpha envelope (`assist_skipping_mode`, `answer_generation_mode: agent`, `tools_spec`) that the current generic route deliberately omits, a two-turn plan-then-run handshake (turn 1 returns a `RESEARCH_PLAN` and mints a session; turn 2, `"Start research"` on that same session, streams the actual run), and a single HTTP connection held open for several minutes delivering six distinct content kinds (`RESEARCH_QUESTION`, `RESEARCH_ANSWER`, `RESEARCH_REPORT`, `RESEARCH_AUDIO_SUMMARY`, plus the plan and a terminal echo). None of this fits the existing `/api-explorer/stream-assist` route or `ApiExplorer.tsx` UI, which are single-shot, stateless, and render one text blob per call. Sending the current minimal envelope to `deep_research` fails with a `500 INTERNAL` (verified live against `hmak-search-engine-genai`), so today the agent is unusable from this app.

Separately, this engine's agent catalog also contains A2A-wrapped agents (e.g. "Antigravity Agent", "Beauty") alongside no-code/low-code workflow agents and the managed `deep_research` agent. This app has not implemented or verified A2A invocation through the Assist endpoint, and Google's A2A agent contract (external `AgentCard`, its own auth/transport) is a materially different integration than the no-code/managed agents this explorer already drives. That gap needs to be an explicit, enforced scope boundary rather than a silent gap a user discovers via an error.

## What Changes

- New dedicated backend route(s) and a new frontend surface implementing the `deep_research` two-phase protocol: mint/track a session across the plan and run turns, send the required v1alpha envelope, and forward the multi-minute chunk stream to the client incrementally rather than buffering the whole run.
- New UI treatment per content kind: render the plan distinctly from the running question/answer trace, the final report with its inline citations, and surface (or explicitly stub, if unresolved) the audio summary reference.
- Agent selection in the UI is restricted to invokable types: no-code/low-code workflow agents and the managed `deep_research` agent. A2A-defined agents (`a2aAgentDefinition`) returned by `list-agents` are surfaced as read-only/unsupported, never offered as an interactive target of the Assist flow.
- All other agents keep the existing standard single-shot `stream-assist` flow, byte-for-byte unchanged — this change adds a second, parallel interaction path for `deep_research` only, it does not touch the generic route's request contract.
- **BREAKING**: none — this is additive; no existing route signature or response shape changes for non-`deep_research` agents.

## Capabilities

### New Capabilities
- `deep-research-assist`: the two-phase plan/run orchestration flow used exclusively for the `deep_research` agent — envelope construction, session continuity across turns, long-lived stream handling, and per-content-kind rendering.
- `assist-agent-scope`: which agent definition types this app will invoke through the Gemini Enterprise Assist endpoint (no-code/low-code workflow agents, the managed `deep_research` agent) versus which it explicitly will not (A2A-defined agents), and how the UI reflects that boundary.

### Modified Capabilities
- (none — the standard single-shot flow's requirements are unchanged; only which agents are offered through the picker is newly constrained by `assist-agent-scope`)

## Impact

- **Backend**: `backend/api/routes/api_explorer.py` gains new route(s) for the deep-research turn sequence (distinct from `stream_assist`, which stays as-is for other agents); likely needs a small in-process session/turn store keyed to the UI session so turn 2 can be issued without the client re-supplying full state.
- **Frontend**: `ApiExplorer.tsx` / `ChatInterface.tsx` gain a `deep_research`-specific view (plan display, live question/answer trace, report render with citations, audio placeholder); the agent picker filters or annotates by agent definition kind.
- **No changes** to `ConversationClient`/`AgentClient` (the classic ConversationalSearch path) or to the existing `stream-assist` route/schema used by every other agent.
- **Open/unresolved**: the endpoint that resolves a `RESEARCH_AUDIO_SUMMARY` `fileId` into playable audio has not been identified; scoped as a spike/task, not blocking the rest of the flow.
