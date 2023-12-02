# Use the official Python image from the Docker Hub
FROM python:3.12-slim

WORKDIR /code

# Copy the poetry files and install dependencies
COPY pyproject.toml poetry.lock /code/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install

COPY . /code

# Expose the port that FastAPI will run on
EXPOSE 8000

# Run the Python app
CMD ["sh", "-c", "export PATH=$PATH:/code/.venv/bin && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
