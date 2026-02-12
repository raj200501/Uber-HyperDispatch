.PHONY: bootstrap verify demo dev

bootstrap:
	bash scripts/verify.sh bootstrap

verify:
	bash scripts/verify.sh verify

demo:
	bash scripts/demo.sh

dev:
	bash scripts/dev.sh
