.PHONY: doctor validate catalog catalog-check dry-run plan links compile test install-dev

install-dev:
	python3 -m pip install -e .

doctor:
	./craft doctor

validate:
	./craft validate

catalog:
	./craft catalog --format md --output docs/skill-catalog.md

catalog-check: catalog
	git diff --exit-code docs/skill-catalog.md

dry-run:
	./craft orchestrate examples/plan.json --dry-run

plan:
	python3 scripts/validate-plan.py examples/plan.json

links:
	python3 scripts/check-markdown-links.py .

compile:
	python3 -m compileall -q src scripts

test: doctor validate catalog plan dry-run links compile
