.PHONY: doctor validate catalog dry-run test install-dev

install-dev:
	python3 -m pip install -e .

doctor:
	./craft doctor

validate:
	./craft validate

catalog:
	./craft catalog --format md --output docs/skill-catalog.md

dry-run:
	./craft orchestrate examples/plan.json --dry-run

plan:
	python3 scripts/validate-plan.py examples/plan.json

test: doctor validate catalog plan dry-run
