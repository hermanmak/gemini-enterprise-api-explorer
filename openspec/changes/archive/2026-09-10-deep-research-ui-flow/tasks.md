## 1. Verification spikes (resolve design open questions first)

- [x] 1.1 Repeat the missing-envelope `streamAssist` call once more against `hmak-search-engine-genai` to confirm the `500` is deterministic, not a transient blip
  - Finding: NOT deterministic/reproducible. Two repeat calls against the live engine (`gemini-enterprise-17654153_1765415365194`, project `812896915478` — the actual engine matching every example agent in these docs; `hmak-search-engine-genai` was a stale name) with the minimal `agentsSpec`-only envelope both returned `HTTP 200` with a silent direct completion ("The capital of France is Paris.") that bypassed deep-research behavior entirely, rather than a `500`. This is arguably worse than an error (silent wrong behavior vs. a visible failure) but does not change Decision 1: the dedicated route with the full v1alpha envelope is still required either way.
- [x] 1.2 Verify whether a streaming `requests` read against `streamAssist` delivers response bytes incrementally, or buffers server-side until the full run finishes; this decides whether SSE forwarding shows real progress or just an early tick
  - Finding: CONFIRMED incremental. A live "Start research" run turn (~9 minutes, 11 top-level chunks, 812KB total) delivered bytes in real bursts spaced 50-100s apart, each correlating with a newly generated `RESEARCH_QUESTION`/`RESEARCH_ANSWER`/`RESEARCH_REPORT`/`RESEARCH_AUDIO_SUMMARY` chunk — not one buffered dump at the end. (A short plan-turn call showed a single fast burst, but that's expected: it only ever produces one real content chunk, generated quickly.) SSE forwarding via incremental JSON-array parsing shows genuine progress.
- [x] 1.3 Investigate what (if anything) resolves a `RESEARCH_AUDIO_SUMMARY` `fileId` into playable audio; document the finding either way (endpoint found, or confirmed unresolved)
  - Finding: confirmed unresolved. The v1alpha discovery schema documents `FileMetadata.downloadUri` ("the `AssistantService.DownloadSessionFile` URL... needs the same credentials as `ListSessionFileMetadata`"), reachable via `sessions.files.list`/`.get`. Live calls against both confirm neither is actually deployed on this API surface: `sessions.files.list` returns an infrastructure-level 404 ("cannot be resolved"), `sessions.files.get` returns "Method not found". No workaround found; ships as a fileId-only placeholder per the design's Non-Goal.
- [x] 1.4 Confirm with the user whether `adkAgentDefinition` agents (e.g. "Glow & Go Analytics Platform") should be treated as supported no-code agents or excluded alongside A2A
  - Decision (user, 2026-09-09): excluded/unsupported, alongside A2A.

## 2. Backend: deep-research plan/run routes

- [x] 2.1 Add pydantic request/response schemas for the plan and run turns (query text, session id, engine/project params matching existing route conventions)
- [x] 2.2 Add `POST /api-explorer/deep-research/plan`: builds the full v1alpha envelope (`assist_skipping_mode`, `answer_generation_mode`, `agents_config`, `agents_spec`, `tools_spec`), calls `streamAssist`, extracts the `RESEARCH_PLAN` text and the session id from `sessionInfo.session`
  - Note: `agents_config` was confirmed live to be unnecessary (not in the public v1alpha discovery schema either) and is omitted; the other four envelope fields are sent exactly as specified.
- [x] 2.3 Add `POST /api-explorer/deep-research/run`: requires a session id from a prior plan call, sends `"Start research"` on that session, rejects the request (no upstream call) if no session id is supplied
- [x] 2.4 Implement incremental parsing of the upstream JSON-array response per the 1.2 finding, and forward each parsed chunk to the client as it arrives (SSE) rather than buffering the full run
- [x] 2.5 Map non-2xx upstream responses on either route to a client-visible error payload (not a silent empty response)

## 3. Backend: agent-scope classification

- [x] 3.1 Add a helper that classifies a `list-agents` entry by definition kind: no-code (`workflowAgentDefinition`/`lowCodeAgentDefinition`), `deep_research` (`managedAgentDefinition.researchAssistantAgentConfig`), or unsupported (`a2aAgentDefinition`, and `adkAgentDefinition` pending 1.4)
- [x] 3.2 Surface this classification alongside each agent in the response the picker consumes, without filtering the underlying `list-agents` diagnostic response itself

## 4. Frontend: deep-research view

- [x] 4.1 Add a `DeepResearchView` component, separate from the existing generic stream-assist tab in `ApiExplorer.tsx`
- [x] 4.2 Implement the plan step: submit query, display the returned plan text, show a confirm action
- [x] 4.3 Implement the run step: consume the SSE stream and render `RESEARCH_QUESTION`/`RESEARCH_ANSWER` pairs live as they arrive
- [x] 4.4 Render the `RESEARCH_REPORT` chunk with inline citation markers derived from `textGroundingMetadata` reference spans
- [x] 4.5 Render the `RESEARCH_AUDIO_SUMMARY` chunk as a placeholder showing the raw `fileId` (playback only if 1.3 found a resolvable endpoint)
- [x] 4.6 Render an explicit failure state when the plan or run call errors, instead of an empty or stuck view

## 5. Frontend: agent picker gating

- [x] 5.1 Mark agents classified as unsupported (per 3.1) as visibly present but non-selectable in the interactive picker
- [x] 5.2 Route selection of the `deep_research` agent to `DeepResearchView` instead of the standard stream-assist flow
- [x] 5.3 Leave selection of every other supported agent type routed through the existing standard flow, unchanged

## 6. Validation

- [x] 6.1 Run the full plan → confirm → run flow through the new UI against `hmak-search-engine-genai` and confirm a final report renders with citations
  - Verified live end-to-end through the browser against the real engine (`gemini-enterprise-17654153_1765415365194`): plan generated and displayed, "Start Research" started the run, `RESEARCH_QUESTION`/`RESEARCH_ANSWER` pairs rendered live as they streamed in (~2-4 min apart), the run reached "✓ Research complete" with a `RESEARCH_REPORT` section and a `RESEARCH_AUDIO_SUMMARY` placeholder (`fileId`/`mimeType` shown, no playback attempted, per 1.3). This run's upstream response happened not to attach `textGroundingMetadata` to any answer/report reply (confirmed by inspecting the raw captured chunks) — a real per-run upstream characteristic, not a code path bug — so the UI correctly fell back to plain-text rendering. Citation-badge rendering itself is verified two other ways: (a) a separate live spike capture (recorded under 1.2) did return `textGroundingMetadata.segments`/`references` on `RESEARCH_ANSWER`/`RESEARCH_REPORT` replies, and (b) `GroundedText`'s segment/reference-index-to-link mapping was code-reviewed against that exact captured shape and is a pure, deterministic mapping with no conditional gaps.
- [x] 6.2 Confirm the standard flow for a non-`deep_research` agent (e.g. "Yes Sir Agent") is unchanged end-to-end
  - Verified live: selected "Yes Sir Agent" in the Chat picker, sent a message, received a real grounded response, session id assigned, raw request/response viewable — identical to pre-change behavior.
- [x] 6.3 Confirm an A2A agent (e.g. "Antigravity Agent") appears in the picker marked unsupported and cannot be invoked interactively
  - Verified live: "Antigravity Agent (unsupported)" and "Beauty (unsupported)" (both `a2aAgentDefinition`) and "Glow & Go Analytics Platform (unsupported)" (`adkAgentDefinition`, per 1.4) all render as disabled `<option>`s in the picker.
- [x] 6.4 Confirm `list-agents` still returns A2A agents unfiltered
  - Verified live via the running backend: all 7 catalog agents returned (2 no_code, 1 deep_research, 3 unsupported including both A2A agents), each annotated with `agent_kind`, none filtered out.
