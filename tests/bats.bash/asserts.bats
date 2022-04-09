#!/usr/bin/env bats

setup_file() { load ../helpers/helper; }

@test "status " {
  run true
  [ "$status" -eq 0 ]
}

@test "assert " {
  assert declare -pF assert
}

@test "assert_success " {
  run declare -pF assert_success
  assert_success
}

@test "assert_failure " {
  run false
  assert_failure
}

@test "assert_exist " {
  assert_exist "${BATS_TEST_FILENAME}"
}

@test "assert_line & assert_output " {
  run printf '%s\n' 1 2 3
  assert_success
  assert_line '2'
  assert_output - <<STDIN
1
2
3
STDIN
}

@test "assert_line() looking for line " {
   run echo $'have-0\nhave-1\nhave-2'
   assert_line 'have-1'
 }

@test "assert_line() partial matching " {
 run echo $'have 1\nhave 2\nhave 3'
 assert_line --partial 'have'
}

@test "assert_line() <expected>: returns 0 if <expected> is a line in \`\${lines[@]}' " {
  run printf 'a\nb\nc'
  assert_line --index 1 'b'
}

@test "assert_line() --regexp <regexp>: enables regular expression matching " {
  run printf 'a\n_b_\nc'
  assert_line --regexp '^_'
}
