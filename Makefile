.PHONY: install run-backend run-frontend test docker-up docker-down lint clean

install:
	python3 -m pip install -r requirements.txt
	python3 -m pip install pytest

run-backend:
	python3 -m uvicorn app.main:app --reload --port 8000

run-frontend:
	python3 -m streamlit run frontend/streamlit_app.py

test:
	python3 -m pytest tests/ -v

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -f reports/*.pdf
