# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in AI Compliance Copilot, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email: [security@your-org.com]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a timeline for resolution.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x     | Yes       |
| 1.x     | No        |

## Security Considerations

- The mock evaluator does not transmit data externally. When `USE_REAL_LLM=true`, system descriptions are sent to the configured LLM provider.
- Input is validated and length-capped to prevent abuse.
- Prompt injection detection flags suspicious inputs but is not a guarantee against all attacks.
- No PHI, PII, or credentials are stored by the application. All analysis is stateless.
- CORS is configured permissively by default (`*`). Restrict `allow_origins` in production.
- API keys should be stored in environment variables, never committed to source control.
