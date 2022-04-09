#!/usr/bin/env bats

setup_file() {
  load ../helpers/helper
  touch "${BATS_TMP}/foo"
}

@test "\$BATS_TMP/foo " {
  assert_file_exist "${BATS_TMP}/foo"
}

@test "\$BATS_TMP/foo persists" {
  assert_file_exist "${BATS_TMP}/foo"
}

@test "func::exported assert_file_exist " {
  run ${BATS_TEST_DESCRIPTION}
  assert_success
}

@test "func::exported bats::array " {
  run ${BATS_TEST_DESCRIPTION}
  assert_success
}
