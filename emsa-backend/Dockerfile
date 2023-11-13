# Use the official Python image from the Docker Hub
FROM python:3.12-slim

WORKDIR /code

# Copy the poetry files and install dependencies
COPY pyproject.toml poetry.lock /code/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY . /code

# Install Flake8, isort, black, and pytest
RUN pip install flake8 isort black pytest pytest-asyncio

# Add the virtual environment to the PATH
ENV PATH="/code/.venv/bin:${PATH}"

# Expose the port that FastAPI will run on
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
