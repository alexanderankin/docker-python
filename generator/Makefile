ROOT := $(abspath $(CURDIR)/..)
UV ?= uv

all: generate

.PHONY: generate
generate:
	$(UV) run --project "$(CURDIR)" python -m docker_python_generator "$(ROOT)/docker-engine-api-specs/v1.40.yaml" "$(ROOT)/versions/v1.40"
	$(UV) run --project "$(CURDIR)" python -m docker_python_generator "$(ROOT)/docker-engine-api-specs/v1.44.yaml" "$(ROOT)/versions/v1.44"
	$(UV) run --project "$(CURDIR)" python -m docker_python_generator "$(ROOT)/docker-engine-api-specs/v1.55.yaml" "$(ROOT)/versions/v1.55"

.PHONY: clean
clean:
	$(UV) run --project "$(CURDIR)" python -m docker_python_generator.clean "$(ROOT)/versions/v1.40" "$(ROOT)/versions/v1.44" "$(ROOT)/versions/v1.55"

.PHONY: regenerate
regenerate: clean
	$(MAKE) -f "$(CURDIR)/Makefile" generate
