.PHONY: setup test demo clean lint typecheck docs

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt

test:
	. .venv/bin/activate && pytest -q

lint:
	. .venv/bin/activate && pylint $$(find . -name '*.py' -not -path './.venv/*') --exit-zero

typecheck:
	. .venv/bin/activate && mypy $$(find . -name '*.py' -not -path './.venv/*')

docs:
	. .venv/bin/activate && pdoc --force --html $$(find . -maxdepth 1 -name '*.py' -print) --output-dir docs/

demo:
	. .venv/bin/activate && python umlement.py demo --recursive --format svg

clean:
	rm -rf .pytest_cache .mypy_cache models docs/*.html docs/*/*.html
