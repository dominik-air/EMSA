## Backend part of emsa project
## Getting Started

### Prerequisites

- Docker
- [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/dominik-air/EMSA.git
    ```

2. Change into the project directory:

    ```bash
    cd ...\EMSA\emsa-backend
    ```

3. Build the Docker image:

    ```bash
    make build
    ```

4. Run the project:

    ```bash
    make run
    ```

The application will be accessible at [http://localhost:8000/](http://localhost:8000/).

### Development

#### Adding package
If you want to add some package just add it to `pyproject.toml` under the
`[tool.poetry.dependencies]` section and install it with  command:
```bash
poetry install
```
useful might be also:
```bash
poetry update
```

#### ! Before creating PR please use make lint and make test !

## Commands

- **Build the Docker image:**

    ```bash
    make build
    ```

- **Run the project:**

    ```bash
    make run
    ```

- **Stop the project:**

    ```bash
    make stop
    ```

- **Clean up (stop and remove containers, including volumes):**

    ```bash
    make clean
    ```

- **Lint the code (format with isort and black, and check with flake8):**

    ```bash
    make lint
    ```

- **Run tests:**

    ```bash
    make test
    ```

- **Run all (lint and test):**

    ```bash
    make all
    ```

- **View logs (follow logs of the running application):**

    ```bash
    make logs
    ```