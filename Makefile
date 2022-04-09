.PHONY: bats publish tests version

SHELL := $(shell bash -c 'command -v bash')
#msg := fix: completions
export msg

brew:
	@brew list bash &>/dev/null || brew bundle --file tests/Brewfile --quiet --no-lock | grep -v "^Using" >/dev/null

publish: tests
	@git add .
	@git commit --quiet -a -m "$${msg:-auto}" || true
	@git push --quiet

tests: brew
	@bin/bats.bash run

