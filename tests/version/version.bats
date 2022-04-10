#!/usr/bin/env bats

setup_file() {
  load ../helpers/helper
  export HELP_LINE="svu wrapper and version management (local and GitHub Actions)"
  export HELP_SVU="semantic version util"
}

setup() {
  . mreleaser.bash
  REMOTE="${BATS_TEST_TMPDIR}/remote.git"
  REPO="${BATS_TEST_TMPDIR}/repo"
  git init --bare --quiet "${REMOTE}"
  git init --quiet "${REPO}"
  cd "${REPO}" || return
  touch README.md
  git add README.md
  git commit --quiet -m "first commit"
  git branch -M main
  git remote add origin "${REMOTE}"
  git push --quiet -u origin main
}

teardown() {
  rm -rf "${REMOTE}"
  rm -rf "${REPO}"
}

run_description() {
  bats::array
  run "${BATS_ARRAY[@]}"
}

@test "version " {
  run_description
  assert_success
  assert_output --regexp "^[0-9]+\.[0-9]+\.[0-9]+$"
}

@test "version --help " {
  run_description
  assert_success
  assert_line "${HELP_LINE}"
  assert_line "${HELP_SVU}"
}

@test "version -h " {
  run_description
  assert_success
  assert_line "${HELP_LINE}"
  assert_line "${HELP_SVU}"
}

@test "version help " {
  run_description
  assert_success
  assert_line "${HELP_LINE}"
  assert_line "${HELP_SVU}"
}

@test "version invalid " {
  run_description
  assert_failure
  assert_line "${BATS_ARRAY[0]}: ${BATS_ARRAY[1]}: invalid command"
  assert_line "${HELP_LINE}"
  assert_line "${HELP_SVU}"
}

@test "command -v svu " {
  run_description
  assert_success
}

@test "svu " {
  run_description
  assert_success
  assert_equal "${output}" "v$(version)"
}

@test "cd /tmp && version " {
  cd /tmp
  run version
  assert_failure
  assert_output "$(git rev-parse --show-toplevel 2>&1 || true)"
}

@test "version needs " {
  run_description
  assert_failure
  assert_output --partial "0.0.0 == 0.0.0"
}

@test "touch file " {
  run_description
  run version needs
  assert_failure
  assert_output --partial "Dirty Repository"
}

@test "touch file1 " {
  run_description
  run version tag
  assert_failure
  assert_output --partial "Dirty Repository"
}

@test "version needs: clean repo " {
  touch file
  git add file
  git commit --quiet -m "second commit"
  git push --quiet origin main

  run version needs
  assert_failure
  assert_output --partial "0.0.0 == 0.0.0"
}

@test "version tag: clean repo " {
  touch file
  git add file
  git commit --quiet -m "second commit"
  git push --quiet origin main
  run version tag
  if $ACTION; then
    assert_success
    assert_output - <<EOF
::echo::on
::set-output name=BUMPED::false
::set-output name=VERSION::0.0.0
EOF
  else
    assert_failure
    assert_output --partial "0.0.0 == 0.0.0"
  fi
}

@test "version tag " {
  touch file
  git add file
  git commit --quiet -m "fix: second commit"
  git push --quiet origin main

  run_description
  assert_success

  if $ACTION; then
    assert_output - <<EOF
::echo::on
::set-output name=BUMPED::true
::set-output name=VERSION::0.0.1
EOF
  else
    assert_output "0.0.1"
  fi
}
