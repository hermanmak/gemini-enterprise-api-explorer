## ADDED Requirements

### Requirement: Supported agent types for interactive invocation
The system SHALL restrict the agent-selection picker's interactive (invokable) list to no-code agents (`workflowAgentDefinition`, `lowCodeAgentDefinition`) and the `deep_research` managed agent. The system SHALL NOT offer agents defined via `a2aAgentDefinition` as an interactive invocation target through the Gemini Enterprise Assist endpoint.

#### Scenario: Picker lists a no-code agent
- **WHEN** the agent catalog contains an agent with `workflowAgentDefinition` or `lowCodeAgentDefinition`
- **THEN** the picker offers it as selectable for the standard interaction flow

#### Scenario: Picker lists the deep_research agent
- **WHEN** the agent catalog contains the `deep_research` managed agent
- **THEN** the picker offers it as selectable, routed to the deep-research-assist flow instead of the standard flow

#### Scenario: Picker lists an A2A agent
- **WHEN** the agent catalog contains an agent with `a2aAgentDefinition`
- **THEN** the picker displays it as present but marked unsupported, and does not allow it to be selected for an interactive turn

### Requirement: Unsupported agent types remain visible in diagnostics
The system SHALL continue to return every agent from the diagnostic `list-agents` endpoint regardless of definition kind; only the interactive picker applies the supported-type filter.

#### Scenario: Diagnostic listing includes an A2A agent
- **WHEN** a caller requests the `list-agents` endpoint
- **THEN** the response includes A2A-defined agents alongside supported types, unfiltered
