.PHONY: bats publish tests version

SHELL := $(shell bash -c 'command -v bash')
#msg := fix: completions
export msg

publish: tests
	@git add .
	@git commit --quiet -a -m "$${msg:-auto}" || true
	@git push --quiet

tests:
	@. ./bin/mreleaser.bash
	@bats.bash run

