# shellcheck shell=bash

#
# Mreleaser Common Library

set -eu
set -o errtrace

# True if Running as GitHub Action
#
export ACTION

# "true" if $CURRENT different from $VERSION, "false" otherwise
export BUMPED

# Current Version
#
export CURRENT

# True if DEBIAN, otherwise false
#
export DEBIAN=false

# True if macOS, otherwise false
#
export MACOS=true

# Python Package Name from setup.cfg if present
#
export PYPACKAGE

# Version Bumped or Next Version
#
export VERSION

export ITALIC="\033[3m"
export RED="\033[1;31m"
export RESET="\033[0m"

# GitHub Token
#
: "${TOKEN=${GH_TOKEN:-${GITHUB_TOKEN-}}}"; export TOKEN
: "${GH_TOKEN=${TOKEN-}}"; export GH_TOKEN


#######################################
# install ad checks dependencies
# Globals:
#   GITHUB_PATH
# Arguments:
#   0
#######################################
_deps() {
  if [ "$(uname -s)" != "Darwin" ]; then
    if grep -qi debian /etc/os-release 2>/dev/null; then
      export DEBIAN=true
      if ! has svu; then \
        echo "deb [trusted=yes] https://apt.fury.io/caarlos0/ /" \
          | sudo tee /etc/apt/sources.list.d/caarlos0.list >/dev/null; \
        sudo apt-get update -qq &>/dev/null && sudo apt-get install -qq svu >/dev/null; \
      fi
    fi
    export MACOS=false
  fi

  if command -v brew >/dev/null; then
    brew list bash &>/dev/null || brew bundle --file tests/Brewfile --quiet --no-lock
  fi

  shopt -u inherit_errexit 2>/dev/null || true

  has parallel || { stderr "Failed to install paralell"; return 1; }
  has svu || { stderr "Failed to install svu"; return 1; }
  bats --version | grep -q "Bats " || { stderr "Failed to install bats"; return 1; }
}

#######################################
# set variables
# Arguments:
#  None
#######################################
_vars() {
  if [ "${GITHUB_ACTOR-}" ]; then
    : "${TOKEN?}"
    ACTION=true
    if ! grep -q "name = ${GITHUB_ACTOR}" ~/.gitconfig 2>/dev/null; then
      git config --global user.name "${GITHUB_ACTOR}"
      git config --global user.email "${GITHUB_ACTOR}@example.com"
    fi
  else
    ACTION=false
  fi

  CURRENT="$(svu --strip-prefix current)"
  VERSION="$(svu --strip-prefix next)"

  BUMPED=false
  [ "${CURRENT}" = "${VERSION}" ] || BUMPED=true
  PYPACKAGE="$(awk -F '[= ]' '/^name = / { print $4 }' setup.cfg 2>/dev/null || true)"
}

#######################################
# has command
# Arguments:
#   1
#######################################
has() { command -v "$1" >/dev/null; }

#######################################
# set GitHub Action output and adds variable to env
# Arguments:
#  None
#######################################
setoutput() {
  echo "::echo::on"
  for arg; do
    echo "::set-output name=${arg}::${!arg}"
    toenv "${arg}"
  done
}

#######################################
# write to stdout and return previous code
# Globals:
#   PWD
# Arguments:
#  None
#######################################
stderr() {
  local rc=$?
  >&2 echo "${RED}x${RESET} ${0##*/}: ${PWD##*/}: ${ITALIC}$*${RESET}"
  return $rc
}

#######################################
# adds variable to $GITHUB_ENV
# Arguments:
#  None
#######################################
toenv() { ! $ACTION || echo "${1}=${!1}" >> "${GITHUB_ENV}"; }

#######################################
# adds value to $GITHUB_PATH
# Arguments:
#  None
#######################################
topath() {
  ! $ACTION || echo "${1}" >> "${GITHUB_PATH}";
  export PATH="${1}:${PATH}"
}


trap "exit 1" SIGUSR1
PID=$$
cd "$(git rev-parse --show-toplevel || kill -SIGUSR1 $PID)"

_deps
_vars

topath "$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd -P)"

