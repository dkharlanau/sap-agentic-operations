# Security Policy

This repository contains public reference material and synthetic examples. It must not contain production access information.

## Never commit

- passwords, tokens, certificates, cookies, or API keys;
- production SAP connection details;
- internal hostnames or VPN details;
- client/customer names when they are not already intentionally public;
- ticket, incident, order, customer, vendor, BP, or employee identifiers from real systems;
- production payloads or screenshots containing confidential data;
- instructions for bypassing authorization or security controls.

## Reference architecture security posture

Examples in this repository assume:

- least-privilege tool access;
- separation of read and write capabilities;
- explicit authorization for state-changing operations;
- typed, narrow execution interfaces;
- audit correlation for important actions;
- verification after execution;
- abstention when policy or evidence is incomplete.

## Reporting

If you find a security issue in repository code added in the future, avoid publishing exploit details in a public issue until a safe disclosure path is available.

For architecture disagreements or improvements that do not expose a vulnerability, a normal GitHub issue is appropriate.
