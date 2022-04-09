#!/usr/bin/env bats

setup_file() { load ../helpers/helper; }

@test "func::exported foo " {
  run func::exported foo
  assert_failure
  assert_line --partial "foo: function not exported"
}

@test "func::exported setup_file " {
  run func::exported setup_file
  assert_failure
  assert_line --partial "setup_file: function not exported"
}

@test "func::exported valid " {
  valid() { :; }; export -f valid
  run func::exported valid
  assert_success
}
