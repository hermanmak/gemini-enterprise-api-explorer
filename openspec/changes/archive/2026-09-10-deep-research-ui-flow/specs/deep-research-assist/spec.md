## ADDED Requirements

### Requirement: Plan turn initiation
The system SHALL send the full v1alpha `streamAssist` envelope (`assist_skipping_mode`, `answer_generation_mode`, `agents_config`, `agents_spec`, `tools_spec`) when a user submits a query with the `deep_research` agent selected, and SHALL capture the session identifier returned in `sessionInfo.session` for use in the run turn.

#### Scenario: User submits a research question
- **WHEN** a user submits a query with the `deep_research` agent selected
- **THEN** the backend sends the full v1alpha envelope to `streamAssist` and returns the `RESEARCH_PLAN` text plus the minted session id to the client

### Requirement: Run turn continuation
The system SHALL issue a second `streamAssist` call with query text `"Start research"` against the session id returned by the plan turn, and SHALL reject a run request that has no prior plan session id.

#### Scenario: User confirms the plan
- **WHEN** a user confirms the plan for a session that has a session id from a prior plan call
- **THEN** the backend issues `"Start research"` on that session and begins streaming the run response to the client

#### Scenario: Run requested without a plan session
- **WHEN** a run request is made without a session id from a prior plan call
- **THEN** the backend rejects the request rather than sending a malformed query to `streamAssist`

### Requirement: Incremental chunk delivery
The system SHALL forward each parsed response chunk from the upstream run call to the client as it is received, rather than buffering the full response before responding.

#### Scenario: Chunk arrives mid-run
- **WHEN** the upstream `streamAssist` call for a run turn produces a new chunk
- **THEN** the client receives that chunk without waiting for the run to fully complete

### Requirement: Content-kind-aware rendering
The UI SHALL render `RESEARCH_PLAN`, `RESEARCH_QUESTION`, `RESEARCH_ANSWER`, `RESEARCH_REPORT`, and `RESEARCH_AUDIO_SUMMARY` chunks with distinct, kind-appropriate presentation, and SHALL render citation markers derived from a `RESEARCH_REPORT` chunk's `textGroundingMetadata`.

#### Scenario: Report chunk received
- **WHEN** a `RESEARCH_REPORT` chunk arrives
- **THEN** the UI renders the report text with inline citation markers derived from the `textGroundingMetadata` reference spans

#### Scenario: Audio summary chunk received
- **WHEN** a `RESEARCH_AUDIO_SUMMARY` chunk arrives
- **THEN** the UI displays a placeholder referencing the file id without attempting playback

### Requirement: Upstream failures are surfaced, not silent
The system SHALL treat a non-2xx response from a `deep_research` plan or run call as a visible error state in the UI.

#### Scenario: Upstream returns an error
- **WHEN** the plan or run call receives a non-2xx response from `streamAssist`
- **THEN** the UI shows an explicit failure state to the user rather than an empty or hung view
