# Mapping SAO to the SAP Agent Ecosystem

SAP Agentic Operations is not an SAP product extension and does not require SAP software to run. This mapping explains where the project's vendor-neutral control concepts fit around the current SAP agent stack.

| SAO concern | SAP ecosystem anchor | Why it matters |
|---|---|---|
| business/process context | SAP Business Data Cloud, SAP Knowledge Graph, SAP Domain Models | models need business semantics, not isolated records |
| agent construction/orchestration | Joule Studio; low-code/pro-code; n8n integration | agent framework is an implementation choice |
| tools | Joule Skills, MCP servers, application APIs | tools expose capability; they do not define business authorization |
| runtime isolation | Joule Studio runtime and platform controls | runtime containment is separate from model reasoning |
| agent/MCP inventory | SAP AI Agent Hub | agents and MCP servers become governed enterprise assets |
| architecture ownership | SAP LeanIX / AI Agent Hub relationships | owner, application, capability and risk context matter |
| process observability | SAP Signavio / platform observability surfaces | agent impact should be measured at process level |
| lifecycle/governance | SAP AI Agent Hub, platform lifecycle services | agents need approval state, ownership, verification and retirement |
| external interoperability | MCP, A2A and other open standards | enterprise controls must survive transport/framework changes |

## Where SAO deliberately sits

```text
      SAP / non-SAP agent frameworks and studios
          Joule Studio / LangGraph / n8n / etc.
                         |
                         v
                 SAO DECISION CONTRACT
                         |
       +-----------------+------------------+
       | identity | evidence | policy | risk |
       +-----------------+------------------+
                         |
                 SAO WRITE ENVELOPE
                         |
                         v
             MCP / Skill / API / Tool layer
                         |
                         v
                 SAP / non-SAP systems
```

SAO is most useful at the boundary between **reasoning** and **enterprise state**.

## What SAO does not duplicate

- It is not another agent builder.
- It is not a replacement for SAP AI Agent Hub.
- It is not an MCP server registry.
- It is not an SAP authorization system.
- It is not an ERP simulator intended to reproduce S/4HANA.

Instead, SAO gives teams a portable way to ask:

1. Was object identity resolved?
2. Is the evidence sufficient and current?
3. Is the proposed action inside the agent's capability?
4. What deterministic policy says the action is allowed?
5. Is approval bound to the exact current state?
6. Can the operation be executed through a narrow tool?
7. Can the business outcome be verified and reversed/compensated?

Those questions remain valid whether the implementation uses Joule Studio, a custom BTP runtime, an external framework, or a mixed enterprise agent estate.
