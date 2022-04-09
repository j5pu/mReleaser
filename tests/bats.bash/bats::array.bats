#!/usr/bin/env bats

setup_file() { load ../helpers/helper; }

@test "bats::array " {
  ${BATS_TEST_DESCRIPTION}
  assert_equal "$(printf '%s ' "${BATS_ARRAY[@]}")" "${BATS_TEST_DESCRIPTION}"
}

@test "bats::array foo boo " {
  bats::array "foo boo"
  assert_equal "${#BATS_ARRAY[@]}" 2
}

@test "bats::array 1 2 3 " {
  bats::array
  assert_equal "${#BATS_ARRAY[@]}" 4
}
