#!/usr/bin/env bats

setup_file() { load ../helpers/helper; }

@test "\$PATH fixtures " {
  was=true
  test -d "${BATS_TESTS}/fixtures" || { was=false; mkdir "${BATS_TESTS}/fixtures"; }
  bats::envrc
  run echo "${PATH}"
  assert_output --regexp "${BATS_TESTS}/fixtures"
  $was || rm -r "${BATS_TESTS}/fixtures"
}

@test "\$PROJECT_DIR " {
  assert_equal "${PROJECT_DIR}" "${BATS_TOP}"
}

@test ".env " {
  unset BATS_BASH
  bats::envrc
  while read -r var; do
    assert [ -n "${!var}" ]
    run declare -p "${var}"
    assert_output --regexp "declare -x ${var}="
  done < <(awk -F '=' '{ print $1 }' "${BATS_TOP}")
}
