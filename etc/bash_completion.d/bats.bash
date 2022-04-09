# shellcheck shell=bash disable=SC2207

#######################################
# bats.bash completions
# Globals:
#   COMPREPLY
# Arguments:
#   1     name of the command whose arguments are being completed
#   2     word being completed ("cur")
#   3     word preceding the word being completed or $1 when is the first word ("prev")
#######################################
_bats_bash() {
  [ "$1" = "$3" ] || return 0
  COMPREPLY=($(compgen -o nospace -W "$("$1" commands; printf '%s\n' -h --help)" -- "$2"))
}

complete -F _bats_bash bats.bash
