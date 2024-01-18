SHELL:=/bin/bash
run:
	python3 app/main.py

test:
	pytest

build:
	bash scripts/docker-build.sh