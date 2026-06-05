# Security Policy

## Supported Versions

The current `main` branch and the latest released minor version receive security
fixes.

## Reporting a Vulnerability

Do not open a public issue for secrets, credential leaks, command injection,
sandbox escape, or other sensitive vulnerabilities.

Use GitHub private vulnerability reporting:

<https://github.com/woogi-kang/craft-harness/security/advisories/new>

Include:

- affected version or commit
- reproduction steps
- expected impact
- suggested fix if available

## Secret Handling

The public repository must not contain:

- API keys or tokens
- private keys or certificates
- local model/provider credentials
- personal workspace logs
- customer project files
