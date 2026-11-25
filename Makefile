PYTHON ?= python3

.PHONY: check test
check: test

test:
	$(PYTHON) -m unittest discover -s tests -v
