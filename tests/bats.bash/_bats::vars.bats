#!/usr/bin/env bats

setup_file() { load ../helpers/helper; }

@test "\$BATS_* " {
  for i in BATS_BASENAME BATS_PATH BATS_TESTS BATS_TMP BATS_TOP; do
    assert [ -n "${!i}" ]
  done
}

@test "\$BATS_* directories " {
  for i in BATS_TESTS BATS_TMP BATS_TOP; do
    assert_dir_exist "${!i}"
  done
}

@test "\$BATS_TOP " {
  assert_equal "${BATS_TOP}" "$(git rev-parse --show-toplevel)"
}

@test "\$BATS_BASENAME " {
  assert_equal "${BATS_BASENAME}" "$(basename "${BATS_TOP}")"
}

@test "\$BATS_* set once per file " {
  unset BATS_TOP
  load ../helpers/helper
  assert [ -z "${BATS_TOP}" ]
}
