install:
	pipenv install --dev
	pipenv install -e .

local-pytest-image:
	docker build --no-cache -t pcic/sdpb-local-pytest -f docker/local-pytest/Dockerfile .

local-pytest-run:
	py3clean .
	docker run --rm -it -v $(shell pwd):/codebase pcic/sdpb-local-pytest
