# Changelog

All notable changes to AI Compliance Copilot are documented here.

## [2.1.0] - 2026-03-30

### Added
- Docker and docker-compose support for containerized deployment
- Pytest test suite covering engine, risk scoring, utils, and API
- `.env.example` for environment configuration
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`
- `.gitignore` for clean repository hygiene
- `Makefile` for common development commands
- Request ID tracking in API responses
- Structured error responses with consistent format
- Streamlit sidebar with framework descriptions and project info
- Multi-framework comparison support in frontend

### Improved
- README with badges, Docker instructions, API documentation, and contributing guide
- Architecture docs with deployment section
- Prompt design docs with extension guide

## [2.0.0] - 2026-03-30

### Added
- Multi-framework support: NIST AI RMF, HIPAA, NIST CSF, FedRAMP, ISO 27001, OWASP LLM Top 10, GDPR
- Modular prompt system with base + framework-specific prompts
- Prompt builder for assembling evaluation prompts
- LLM client with mock and real OpenAI integration
- Risk scoring module with summary generation
- 70 compliance controls across 7 frameworks
- Per-control evidence, gaps, and recommendations in output
- `/frameworks` API endpoint

### Changed
- Restructured from monolithic engine to modular architecture
- Upgraded response schema with risk_summary, evidence_found, gaps

## [1.0.0] - 2026-03-30

### Added
- Initial release
- FastAPI backend with `/analyze` endpoint
- NIST AI RMF and HIPAA support
- Streamlit frontend
- PDF report generation
- Prompt injection detection
