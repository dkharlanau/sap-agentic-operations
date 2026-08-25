# State of Practice — Enterprise Agents around SAP

**Evidence date: 2026-08-25**

This note records the external architecture signals that shape SAP Agentic Operations. It is not official SAP guidance and it does not claim product behavior beyond the linked primary sources.

## 1. SAP has moved from isolated copilots toward an agent platform

At SAP Sapphire 2026, SAP described the new Joule Studio as a managed environment for building agents, applications, and workflows with business context, low-code and pro-code development, n8n orchestration, a managed runtime, observability, and governance integration.

Source: [SAP News — Announcing New Joule Studio for Enterprise Scale Agentic Development, 2026-05-13](https://news.sap.com/2026/05/new-joule-studio-enterprise-scale-agentic-development/)

**Implication for this repository:** framework-specific agent construction is no longer the interesting gap. The durable problem is how to express and test control boundaries across frameworks and runtimes.

## 2. MCP is already part of SAP's agent-builder surface

SAP's Joule Studio classic-edition documentation explicitly describes adding MCP servers and tools to Joule agents. The same documentation supports structured JSON/Data Type outputs that are preserved without conversational rewriting.

Sources:

- [SAP Learning — Building Joule agents with Joule Studio, classic edition](https://learning.sap.com/courses/getting-started-with-joule-studio-classic-edition/building-joule-agents-with-joule-studio-classic-edition_c0cc36a2-6f76-4d03-b6d0-abed14a82eda)
- [SAP Help — Create a Joule Agent](https://help.sap.com/docs/joule-studio-classic/joule-studio-classic-edition/create-joule-agent)

**Implication:** MCP should be treated as a tool transport, not as a security model. SAO keeps authorization, policy, write envelopes, and verification above the transport layer.

## 3. Agent governance is becoming an enterprise-architecture problem

SAP AI Agent Hub is documented as a vendor-agnostic command center for discovering and governing AI agents, LLMs, and MCP servers. Its model links agents to business capabilities, organizations, applications, interfaces, models, ownership, risk, governance state, and business value.

Sources:

- [SAP Help — SAP AI Agent Hub](https://help.sap.com/docs/leanix/ea/ai-agent-hub)
- [SAP Help — Key Concepts: SAP AI Agent Hub](https://help.sap.com/docs/leanix/ea/key-concepts-sap-ai-agent-hub?lang=en)
- [SAP Business AI Q2 2026 release highlights](https://news.sap.com/2026/07/sap-business-ai-release-highlights-q2-2026/)

**Implication:** a serious public reference project should model agents as governed enterprise assets, not just code. SAO therefore separates business risk tier, capability level, evidence, policy, and execution.

## 4. SAP's architecture direction explicitly includes identity, runtime, observability, and open standards

SAP Architecture Center's 2026 AI-native material describes platform responsibilities including runtime, sandboxing, observability, governance, agent lifecycle, identity, routing, integration, resilience, and open standards. SAP also documents its participation in the Linux Foundation Agentic AI Foundation working groups covering accuracy, governance, identity/trust, observability, security/privacy, and workflow/process integration.

Sources:

- [SAP Architecture Center — AI-native North Star Architecture](https://architecture.learning.sap.com/assets/ai-native-north-star-architecture-public-q2-2026.pdf)
- [SAP Architecture Center — Agentic AI Foundation](https://architecture.learning.sap.com/docs/global-standards-for-agentic-ai/agentic-ai-foundation)
- [SAP Architecture Center — SAP's AI Golden Path](https://architecture.learning.sap.com/docs/ai-golden-path)

**Implication:** SAO's control plane is deliberately aligned to these durable concerns while remaining vendor-neutral and runnable without an SAP tenant.

## 5. MCP authorization is still evolving rapidly

The 2026-07-28 MCP specification revision hardened authorization and changed core protocol behavior. Separately, the Enterprise-Managed Authorization extension became stable in June 2026 to support centrally managed enterprise access to MCP servers.

Sources:

- [MCP Blog — The 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [MCP Blog — Enterprise-Managed Authorization, 2026-06-18](https://blog.modelcontextprotocol.io/posts/enterprise-managed-auth/)

**Implication:** SAO should avoid baking transport-era assumptions into business authorization. Tool identity, OAuth scopes, enterprise authorization, business approval, and a state-change envelope are different layers.

## 6. Agentic security has moved beyond prompt injection

OWASP's 2026 agentic work covers autonomous-agent risks such as goal hijacking, tool misuse, identity/privilege abuse, memory/context poisoning, insecure communication, cascading failure, trust exploitation, and rogue behavior. OWASP also published dedicated guidance for secure MCP server development and a 2026 governance/security landscape.

Sources:

- [OWASP — Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [OWASP — State of Agentic AI Security and Governance 2.01](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/)
- [OWASP — Agentic Security Initiative](https://genai.owasp.org/initiatives/agentic-security-initiative/)

**Implication:** the benchmark must test security and operational correctness together. A model that diagnoses correctly but escalates privilege, trusts poisoned memory, or executes on stale state still fails.

## Project direction derived from the evidence

The strongest niche for SAP Agentic Operations is therefore:

> **A vendor-neutral conformance and evaluation lab for agents that reason around enterprise systems of record, using SAP-shaped synthetic operations as the proving ground.**

The project should not compete with Joule Studio, LangGraph, Pydantic AI, n8n, or MCP. It should make implementations built with any of them easier to challenge on enterprise invariants.

That leads to four concrete product surfaces:

1. **SAO Control Plane** — architecture and contracts for identity, evidence, policy, capability, write safety, and verification.
2. **SAO-Bench** — deterministic machine-readable cases for enterprise failure modes.
3. **Synthetic Enterprise Simulator** — a small stateful environment where agents can be tested without a real SAP system.
4. **Adapters** — optional examples showing how different agent runtimes emit the same SAO decision contract.
