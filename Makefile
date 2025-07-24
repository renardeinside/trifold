fmt:
	ruff format .
	ruff check . --fix
	yarn --cwd src/trifold/ui prettier --write .
