IMAGE_NAME = emsa-app
CONTAINER_NAME = emsa-container

.PHONY: build run logs stop clean lint mypy test

build:
	docker-compose build

run start:
	docker-compose up -d

rerun: stop build run

logs log:
	docker-compose logs -f $(IMAGE_NAME)

stop down:
	docker-compose down

lint:
	docker-compose exec $(IMAGE_NAME) isort /src --color
	docker-compose exec $(IMAGE_NAME) black /src --color
	docker-compose exec $(IMAGE_NAME) flake8 /src 

mypy:
	docker-compose exec $(IMAGE_NAME) mypy /src

test:
	docker-compose exec $(IMAGE_NAME) sh -c "pytest /src/tests"

all: lint test mypy