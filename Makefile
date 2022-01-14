FORMATTER=pipenv run python -m black

lint:
	pipenv run python -m flake8

format:
	$(FORMATTER) .

format-check:
	$(FORMATTER) . --check
