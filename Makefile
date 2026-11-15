all:

.venv/.created:
	python -m venv .venv && touch $@

ACTIVATE ?= { source .venv/bin/activate || source .venv/Scripts/activate; }
TOX_ARGS ?=

.venv/.installed: .venv/.created
	$(ACTIVATE); pip install -e ./core
	$(ACTIVATE); pip install --group './core/pyproject.toml:dev'
	$(ACTIVATE); pip install -e ./generator
	$(ACTIVATE); pip install -e ./docker-python-requests
	$(ACTIVATE); python -m docker_python_generator "./docker-engine-api-specs/v1.40.yaml" "./versions/v1.40"
	$(ACTIVATE); python -m docker_python_generator "./docker-engine-api-specs/v1.44.yaml" "./versions/v1.44"
	$(ACTIVATE); python -m docker_python_generator "./docker-engine-api-specs/v1.55.yaml" "./versions/v1.55"
	$(ACTIVATE); pip install -e ./versions/v1.40
	$(ACTIVATE); pip install -e ./versions/v1.44
	$(ACTIVATE); pip install -e ./versions/v1.55
	$(ACTIVATE); pip install -e ./examples
	touch $@

test: .venv/.installed
	$(ACTIVATE); pytest --ignore=itests --durations=10

ty: .venv/.installed
	$(ACTIVATE); ty check \
		--exclude '**/tests/**' \
		--exclude 'itests/**' \
		--extra-search-path core/src \
		--extra-search-path generator/src \
		--extra-search-path docker-python-requests/src \
		--extra-search-path versions/v1.40/src \
		--extra-search-path versions/v1.44/src \
		--extra-search-path versions/v1.55/src \
		--extra-search-path examples/src

integration-test: .venv/.installed
	$(ACTIVATE); pip install ./itests/ --group './itests/pyproject.toml:test'
	$(ACTIVATE); python -m pytest itests -v --durations=10

tox-unit: .venv/.installed
	$(ACTIVATE); tox $(TOX_ARGS)

tox-integration: .venv/.installed
	$(ACTIVATE); tox -m itest $(TOX_ARGS)

.venv/.build-installed: .venv/.created
	$(ACTIVATE); pip install --upgrade pip build

wheels: .venv/.build-installed
	$(ACTIVATE); python -m build ./core/ --wheel -o ./dist
	$(ACTIVATE); python -m build ./docker-python-requests/ --wheel -o ./dist
	$(ACTIVATE); for package in ./versions/*/; do \
	version=$$(basename "$$package"); \
	  python -m docker_python_generator "./docker-engine-api-specs/$$version.yaml" "$$package"; \
	  python -m build "$$package" --wheel -o ./dist; \
	done
