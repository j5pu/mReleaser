#!/usr/bin/env bash

: "${BASH_SOURCE?}"

# <html><h2>Bats Description Array</h2>
# <p><strong><code>$BATS_ARRAY</code></strong> created by bats::description() with $BATS_TEST_DESCRIPTION.</p>
# </html>
export BATS_ARRAY

# <html><h2>Git Top Basename</h2>
# <p><strong><code>$BATS_TOP_NAME</code></strong> basename of git top directory when sourced from a git dir.</p>
# </html>
export BATS_BASENAME

# <html><h2>Saved $PATH on First Suite Test Start</h2>
# <p><strong><code>$BATS_PATH</code></strong></p>
# </html>
export BATS_PATH

# <html><h2>Git Top Tests Path (Super Project)</h2>
# <p><strong><code>$BATS_TESTS</code></strong> git top tests directory based on $PWD (tests, test or __tests__.</p>
# </html>
export BATS_TESTS

# <html><h2>Bats File Tmp Directory to Persists in Parallel</h2>
# <p><strong><code>$BATS_TMP</code></strong> alias of $BATS_FILE_TMPDIR.</p>
# <a href="https://bats-core.readthedocs.io/en/stable/writing-tests.html#special-variables">$BATS_FILE_TMPDIR</a>
# </html>
export BATS_TMP

# <html><h2>Git Top Path</h2>
# <p><strong><code>$BATS_TOP</code></strong> contains the git top directory using $PWD.</p>
# </html>
export BATS_TOP

#######################################
# BATS CORE VARIABLES
#######################################

# <html><h2>Add timing information to tests </h2>
# <p><strong><code>$BATS_ENABLE_TIMING</code></strong>.</p>
# <p><strong><code>bats --timing</code></strong></p>
# <a href="https://bats-core.readthedocs.io/en/stable/usage.html#parallel-execution">parallel-execution</a>
# </html>
export BATS_ENABLE_TIMING

# Library directory:
# Applications/PyCharm.app/Contents/bin/plugins/bashsupport-pro/bats-core/libexec/bats-core
export BATS_LIBEXEC

# <html><h2>Serialize test file execution instead of running them in parallel </h2>
# <p><strong><code>$BATS_NO_PARALLELIZE_ACROSS_FILES</code></strong> (requires --jobs >1).</p>
# <p><strong><code>bats --no-parallelize-across-files</code></strong></p>
# <a href="https://bats-core.readthedocs.io/en/stable/usage.html#parallel-execution">parallel-execution</a>
# </html>
export BATS_NO_PARALLELIZE_ACROSS_FILES

# <html><h2>Disable Parallelize within a single file </h2>
# <p><strong><code>$BATS_NO_PARALLELIZE_WITHIN_FILE</code></strong> true (bool) in 'setup_file()' disables for file.</p>
# <p><strong><code>bats --no-parallelize-within-files</code></strong></p>
# <a href="https://bats-core.readthedocs.io/en/stable/usage.html#parallel-execution">parallel-execution</a>
# </html>
export BATS_NO_PARALLELIZE_WITHIN_FILE

# <html><h2>Number of parallel jobs (requires GNU parallel) </h2>
# <p><strong><code>$BATS_NUMBER_OF_PARALLEL_JOBS</code></strong></p>
# <p><strong><code>bats --jobs <jobs></code></strong></p>
# <a href="https://bats-core.readthedocs.io/en/stable/usage.html#parallel-execution">parallel-execution</a>
# </html>
export BATS_NUMBER_OF_PARALLEL_JOBS

# Output file:
# /var/folders/3c/k3_3r82s08q31699vdnxd2s00000gp/T/bats-run-6576/bats.6612.out
export BATS_OUT

# Name (not a file/file):
# /var/folders/3c/k3_3r82s08q31699vdnxd2s00000gp/T/bats-run-7204/bats.7229
export BATS_PARENT_TMPNAME

# The repository of bats-core :
# /Applications/PyCharm.app/Contents/bin/plugins/bashsupport-pro/bats-core
export BATS_ROOT

# Source file generated from the bats file:
# /var/folders/3c/k3_3r82s08q31699vdnxd2s00000gp/T/bats-run-7606/bats.7632.src
export BATS_TEST_SOURCE

# Temp file name under $BATS_RUN_TMPDIR (not created):
# /var/folders/3c/k3_3r82s08q31699vdnxd2s00000gp/T/bats-run-7606/bats.7642
export BATS_TMPNAME

#######################################
# parse arguments when is executed and run bats  (private used by bats.bash)
# Globals:
#   OPTS_BACK
# Arguments:
#   None
#######################################
_bats::run() {
  local args=("${BATS_TESTS}" --jobs "${BATS_NUMBER_OF_PARALLEL_JOBS:-1}" --print-output-on-failure --recursive)
  local output="${BATS_TESTS}/output"

  rm -rf "${output}"

  if [ "${1-}" ]; then
    case "${1-}" in
      commands) printf '%s\n' "$1" list run verbose; exit ;;
      list) files::functions "$(brew --prefix)"/lib/bats-*/src/*.bash "${BASH_SOURCE[0]}" | sort; exit ;;
      run) : ;;
      verbose) args+=(--gather-test-outputs-in "${output}" --no-tempdir-cleanup --output "${output}" \
        --show-output-of-passing-tests --timing --trace --verbose-run) ;;
      *) echo "${0##*/}: $1: invalid argument"; _bats::usage 1 ;;
    esac
  else
    _bats::usage 1
  fi

  exec bats "${args[@]}"
}

#######################################
# bats.bash has been sourced: loads and export bats libs and bats.bash functions (private used by bats.bash)
# Globals:
#   BATS_SUITE_TEST_NUMBER
# Arguments:
#  None
# Returns:
#   0 ...
#######################################
_bats::sourced() {
  local i lib
  lib="$(brew --prefix)/lib"
  for i in bats-assert bats-file bats-support; do
    source "${lib}/${i}/load.bash" || { echo "${BASH_SOURCE[0]}: ${lib}/${i}/load.bash: sourcing error"; return 1; }
  done
  # shellcheck disable=SC2046
  export -f  $(files::functions "${lib}"/*/src/*.bash "${BASH_SOURCE[0]}")
  func::exported assert || return
  func::exported || return
}

#######################################
# show help and exit
# Arguments:
#   None
#######################################
_bats::usage() {
  cat <<EOF
usage: ${0##*/} list|run|verbose
   or: ${0##*/} -h|--help
   or: . ${0##*/}

update secrets in repositories, login to services, or updates ssh.

Commands:
   commands   display ${0##*/}' commands
   list       display list of functions available when ${0##*/} is sourced
   run        run bats tests for the current directory with \$BATS_NUMBER_OF_PARALLEL_JOBS jobs
   verbose    run bats tests showing all outputs, with trace and not cleaning the tempdir
EOF
  exit "${1:-0}"
}

#######################################
# set bats.bash helper variables (private used by bats.bash)
# Globals:
#   BATS_BASENAME
#   BATS_TMP
#   BATS_TMP_ROOT
#   BATS_TOP
#   BATS_TOP_TESTS
#   PWD
# Arguments:
#  None
# Returns:
#   0 ...
#   <unknown> ...
#######################################
_bats::vars() {
  ! func::exported 2>/dev/null || return 0

  cd "$(git rev-parse --show-toplevel)" || exit

  BATS_PATH="${PATH}"

  BATS_TMP="${BATS_FILE_TMPDIR}"

  BATS_TOP="${PWD}"

  BATS_BASENAME="${BATS_TOP##*/}"

  if test -d "${BATS_TOP}/tests"; then
    BATS_TESTS="${BATS_TOP}/tests"
  elif test -d "${BATS_TOP}/test"; then
    BATS_TESTS="${BATS_TOP}/test"
  elif test -d "${BATS_TOP}/__tests__"; then
    BATS_TESTS="${BATS_TOP}/__tests__"
  fi
  : "${BATS_TESTS?No Test Directory in "${BATS_TOP}"}"
}

#######################################
# creates $BATS_ARRAY array from $BATS_TEST_DESCRIPTION or argument
# Globals:
#   BATS_ARRAY
#   BATS_TEST_DESCRIPTION
# Arguments:
#  1    Value (default: $BATS_TEST_DESCRIPTION)
#######################################
bats::array() { read -r -a BATS_ARRAY <<<"${1:-${BATS_TEST_DESCRIPTION}}"; }

#######################################
# running on debian
# Arguments:
#  None
# Returns:
#   1 if not running on debian and 0 if running on debian
#######################################
bats::debian() { test -f /etc/os-release || grep -q debian /etc/os-release; }

#######################################
# changes to $BATS_TOP, restores $PATH to $BATS_PATH, sources .envrc and prepend $BATS_TESTS/fixtures to $PATH
# Globals:
#   PATH
#   PWD
# Arguments:
#  None
#######################################
bats::envrc() {
  cd "${BATS_TOP}"
  PATH="${BATS_PATH}"
  ! test -f ./.envrc || source ./.envrc || { echo "${BASH_SOURCE[0]}: ${BATS_TOP}/.envrc: sourcing error"; return 1; }
  [ ! -d "${BATS_TESTS}/fixtures" ] || PATH="${BATS_TESTS}/fixtures:${PATH}"
}

#######################################
# running as a GitHub action
# Globals:
#   GITHUB_RUN_ID
# Arguments:
#  None
# Returns:
#   1 if not running on GitHub and 0 if running as an action
#######################################
bats::github() { [ "${GITHUB_RUN_ID-}" ]; }

#######################################
# running on macOS
# Arguments:
#  None
# Returns:
#   1 if not running on macOS and 0 if running on macOS
#######################################
bats::macos() { [ "$(uname -s)" = "Darwin" ]; }

#######################################
# get functions in file/files
# Arguments:
#  None
#######################################
files::functions() { awk -F '(' '/^[a-z].*\(\)/ { print $1 }' "$@"; }

#######################################
# checks if function is exported
# Globals:
#   FUNCNAME
# Arguments:
#   1   function name
# Returns:
#   1 if function is not exported, 0 if function is exported
#######################################
func::exported() {
  local arg="${1:-${FUNCNAME[0]}}"
  declare -Fp "${arg}" 2>/dev/null | grep -q "declare -fx ${arg}" >/dev/null \
    || { >&2 echo "${BASH_SOURCE[0]}: ${arg}: function not exported"; return 1; }
}

! [[ ${1-} =~ -h|--help ]] || _bats::usage
_bats::vars
bats::envrc

if [ "${BASH_SOURCE[0]##*/}" = "${0##*/}" ]; then
  set -eu
  shopt -s inherit_errexit
  _bats::run "$@"
else
  _bats::sourced
fi

unset -f  _bats::run _bats::sourced _bats::usage _bats::vars
