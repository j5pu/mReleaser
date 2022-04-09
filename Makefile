.PHONY: bats publish tests version

SHELL := $(shell bash -c 'command -v bash')
#msg := fix: completions
export msg

bats:
	@command -v bats >/dev/null || brew bundle --file tests/Brewfile --quiet --no-lock | grep -v "^Using" >/dev/null
	@bin/bats.bash run

publish: tests
	@git add .
	@git commit --quiet -a -m "$${msg:-auto}" || true
	@git push --quiet

tests:
	@command -v bats >/dev/null || brew bundle --file tests/Brewfile --quiet --no-lock | grep -v "^Using" >/dev/null
	@bin/bats.bash run

