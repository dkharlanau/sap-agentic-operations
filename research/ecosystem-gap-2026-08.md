# Ecosystem Gap — Why SAO Is Not Another SAP Agent Repository

**Review date: 2026-08-25**

The public SAP-agent ecosystem is already developing quickly. SAO should complement it rather than copy it.

## Existing implementation patterns

### SAP MCP access

The public `sap-support/sap-mcp-server` distribution focuses on secure MCP-compatible access to SAP ABAP/BTP services and documents layered controls around SAP access.

https://github.com/sap-support/sap-mcp-server

### SAP BTP / Joule agent samples

SAP publishes runnable industry/custom-agent examples covering Joule Studio, code-based agents and agent integration.

https://github.com/SAP-samples/btp-agentic-ai-use-cases

SAP also publishes pro-code A2A reference implementations for connecting custom agents with Joule on BTP.

https://github.com/SAP-samples/btp-joule-a2a-pro-code-agent

### SAP development-agent grounding

SAP samples demonstrate MCP-grounded coding-agent workflows for CAP/Fiori development.

https://github.com/SAP-samples/cap-agentic-engineered

### Enterprise process automation around SAP

AWS publishes a substantial reference architecture for agentic process automation around SAP that already includes SAP OData via MCP, autonomy controls, approval/ticket flows, pluggable identity, and deterministic Cedar policy enforcement.

https://github.com/aws-samples/sample-agentic-ai-process-automation-for-sap

## The gap SAO should occupy

These projects answer variations of:

- How do I connect an agent to SAP?
- How do I build/deploy an agent?
- How do I orchestrate a business use case?
- How do I ground coding agents in SAP knowledge/tools?

SAO should instead answer:

> **How can different enterprise-agent implementations be challenged against the same operational safety and evidence invariants before they are trusted with systems of record?**

That produces a different artifact:

```text
implementation repositories        SAO
---------------------------        ---------------------------
MCP server                    ->    test excessive capability
Joule / A2A agent             ->    test identity/evidence/policy
AWS process automation        ->    test approval/stale-state behavior
custom LangGraph agent        ->    same benchmark contract
n8n workflow                  ->    same benchmark contract
```

## Defensible differentiation

SAO should build depth in five places:

1. **Portable decision contracts** independent from agent framework.
2. **Adversarial enterprise cases** where the correct output is often restraint.
3. **Stateful synthetic operations** that reproduce stale state, races, retries, and postcondition failures.
4. **Conformance profiles** that make claims explicit (`Diagnostic`, `Write-Safe`, `Auditable`, etc.).
5. **Cross-runtime comparison** using the same benchmark inputs and output schema.

## What not to build

Avoid spending the project's energy on:

- a generic SAP OData/MCP connector;
- an SAP GUI control server;
- another Joule scaffold;
- a generic multi-agent orchestrator;
- an LLM-powered incident chatbot;
- a production SAP integration framework without a unique control/evaluation contribution.

Those areas already have credible public implementations.

## Strong future proof point

A compelling external validation would be:

> The same SAO case pack is run through a Joule Studio agent, a LangGraph agent, and an n8n workflow. All three can solve the business problem, but the benchmark reveals different failures in stale-state handling, evidence provenance, tool scope, or approval binding.

That would make SAO useful as research, architecture guidance, and portfolio evidence at the same time.
