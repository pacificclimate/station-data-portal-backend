.PHONY: install-default
install-default:
	poetry install --dev
	poetry install -e .


.PHONY: local-pytest-image
local-pytest-image:
	docker build \
		--no-cache \
		-t pcic/sdpb-local-pytest \
		-f docker/local-pytest/Dockerfile \
		.

local-pytest-run:
	py3clean .
	docker run --rm -it -v $(shell pwd):/codebase pcic/sdpb-local-pytest
