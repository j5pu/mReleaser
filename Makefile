.PHONY: bats publish tests version

SHELL := $(shell bash -c 'command -v bash')
#msg := fix: completions
export msg

deps:
	@! command -v brew >/dev/null || brew list bash &>/dev/null || brew bundle --file tests/Brewfile --quiet --no-lock
	@if grep -q debian /etc/os-release 2>/dev/null; then \
		echo "deb [trusted=yes] https://apt.fury.io/caarlos0/ /" \
			| sudo tee /etc/apt/sources.list.d/caarlos0.list >/dev/null; \
		sudo apt update -qq &>/dev/null && sudo apt install -qq svu >/dev/null; \
	fi
	@type svu >/dev/null


publish: tests
	@git add .
	@git commit --quiet -a -m "$${msg:-auto}" || true
	@git push --quiet

tests: deps
	@bin/bats.bash run

