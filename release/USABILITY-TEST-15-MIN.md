# 15-minute external usability test

This protocol measures whether a first-time SAP practitioner can run and interpret the synthetic practical toolkit. It does not claim any external test has occurred.

## Participant and privacy boundary

Suitable participant: SAP functional/technical consultant, AMS lead, integration specialist, master-data practitioner, or system analyst unfamiliar with SAO.

Use only `sao demo`. Do not use or publish client names, business-object identifiers, ticket text, hostnames, URLs, credentials, screenshots, or payloads.

## Facilitator script

| Time | Participant task | Observe without coaching |
| --- | --- | --- |
| 0–3 min | Install from the release tag using the [golden quickstart](GOLDEN-QUICKSTART-0.4.0-alpha.3.md). | Setup friction and terminology. |
| 3–6 min | Run `sao demo` and locate the Markdown report. | Time to first useful output. |
| 6–10 min | Explain the selected change, available evidence, classification, and missing evidence. | Whether causality/freshness are understandable. |
| 10–13 min | Identify one safe next action and two blocked shortcuts. | Whether recommendation is confused with authorization. |
| 13–15 min | State what evidence would prove business resolution. | Whether technical success is confused with business outcome. |

Stop if installation consumes more than six minutes. Record the blocker rather than completing the workflow for the participant.

## Blank result record

```text
Release/tag tested:
Operating system and Python version:
Participant role/domain (no employer/client name):
Completed within 15 minutes: yes / no
First blocker:
Classification understood: yes / no / unclear
Unsafe shortcuts identified: 0 / 1 / 2+
Recommendation vs authorization understood: yes / no / unclear
Business resolution evidence understood: yes / no / unclear
Most useful output:
Most confusing term or step:
Suggested improvement:
```

Submit only sanitized findings through the repository's **SAO practical field report** issue form. A blank template, maintainer self-test, or synthetic CI run is not external usability evidence.
