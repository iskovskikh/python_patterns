export FLASK_APP:=./src/allocation/api/flask/flask_app.py
export FLASK_DEBUG:=1

export FASTAPI_PATH:=./src/allocation/api/fastapi
export FASTAPI_APP:=fastapi_app

export PYTHONUNBUFFERED:=1

run-flask:
	flask run --port 8000

run-fastapi:
	uvicorn --app-dir $(FASTAPI_PATH) $(FASTAPI_APP):app --reload --port 8000

test:
	python -m pytest