# Contributing to AI Compliance Copilot

Thanks for your interest in contributing. Here's how to get started.

## Development Setup

```bash
git clone https://github.com/your-org/ai-compliance-copilot.git
cd ai-compliance-copilot
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install pytest
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

## Running Locally

```bash
# Terminal 1: Backend
python3 -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
python3 -m streamlit run frontend/streamlit_app.py
```

## Adding a New Framework

1. Create `app/prompts/your_framework.py` with the framework-specific prompt string
2. Create `data/your_framework_controls.json` with 10+ controls (id, title, description)
3. Add keyword mappings to `app/llm_client.py` in `KEYWORD_MAP`
4. Register the framework in `app/utils.py` (`FRAMEWORK_REGISTRY` and `FRAMEWORK_FILES`)
5. Import and register the prompt in `app/prompts/prompt_builder.py`
6. Add the framework to the Streamlit dropdown in `frontend/streamlit_app.py`
7. Add tests in `tests/`

## Code Standards

- Type hints on all function signatures
- Docstrings on all public functions
- Comments explaining non-obvious logic
- Run `python3 -m pytest tests/ -v` before submitting a PR

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes with tests
4. Run the test suite
5. Submit a PR with a clear description of what changed and why

## Reporting Issues

Use GitHub Issues. Include:
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
