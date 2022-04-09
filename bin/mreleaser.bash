# shellcheck shell=bash

#
# Mreleaser Actions.bash

set -eu
set -o errtrace
shopt -u inherit_errexit

trap "exit 1" SIGUSR1
PID=$$

cd "$(git rev-parse --show-toplevel || kill -SIGUSR1 $PID)"

# True if Running as GitHub Action
#
export ACTION

# True if DEBIAN, otherwise false
#
export DEBIAN=false

# True if macOS, otherwise false
#
export MACOS=true

export ITALIC="\033[3m"
export RED="\033[1;31m"
export RESET="\033[0m"

# GitHub Token
#
: "${TOKEN=${GH_TOKEN:-${GITHUB_TOKEN-}}}"; export TOKEN

#######################################
# has command
# Arguments:
#   1
#######################################
has() { command -v "$1" >/dev/null;}

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

if [ "${GITHUB_ACTOR-}" ]; then
  ACTION=true
  if ! grep -q "name = ${GITHUB_ACTOR}" ~/.gitconfig; then
    git config --global user.name "${GITHUB_ACTOR}"
    git config --global user.email "${GITHUB_ACTOR}@example.com"
  fi
else
  ACTION=false
fi

if [ "$(uname -s)" != "Darwin" ]; then
  if grep -qi debian /etc/os-release 2>/dev/null; then
    export DEBIAN=true
  fi
  export MACOS=false
fi

topath "/home/linuxbrew/.linuxbrew/bin"
has "${0##*/}" || topath "$(cd "$(dirname "$0")"; pwd -P)"
has svu || { stderr "Failed to install svu"; return 1; }
