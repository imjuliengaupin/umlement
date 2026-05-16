.PHONY: setup test demo ui ui-demo-image clean lint typecheck docs verify

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

verify: test typecheck lint

test:
	. .venv/bin/activate && pytest -q

lint:
	. .venv/bin/activate && pylint $$(find . -name '*.py' -not -path './.venv/*') --exit-zero

typecheck:
	. .venv/bin/activate && mypy $$(find . -name '*.py' -not -path './.venv/*' -not -path './scripts/capture_ui_demo.py')

docs:
	. .venv/bin/activate && pdoc --force --html $$(find . -maxdepth 1 -name '*.py' -print) --output-dir docs/

demo:
	. .venv/bin/activate && python umlement.py demo/sample_project --recursive --format svg --progress

ui:
	. .venv/bin/activate && python ui_app.py

ui-demo-image:
	. .capture-venv/bin/activate && python scripts/capture_ui_demo.py

clean:
	rm -rf .pytest_cache .mypy_cache models docs/*.html docs/*/*.html
