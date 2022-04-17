# [mreleaser](https://github.com/j5pu/mreleaser)

![shrc](./.idea/icon.svg)

[![Build Status](https://github.com/j5pu/mreleaser/workflows/main/badge.svg)](https://github.com/j5pu/mreleaser/actions/workflows/main.yaml)

[![tap](https://github.com/j5pu/homebrew-tap/workflows/main/badge.svg)](https://github.com/j5pu/homebrew-tap/actions)

Multi Language Releaser Action and Scripts

## [action](./action.yml)

### Examples:

```yaml
name: main

on:
  push:
  release:
  workflow_dispatch:

env:
  GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}

jobs:
  tests:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: true
      matrix:
        os: [ macos-latest, macos-10.15, ubuntu-latest, ubuntu-18.04 ]
    steps:
      - uses: actions/checkout@main
      - uses: Homebrew/actions/setup-homebrew@master
      - run: make tests

  release:
    needs: [ tests ]
    runs-on: ubuntu-latest
    steps:
      - uses: j5pu/mReleaser@main
```

```mermaid
flowchart TD;
    A[push] --> B[tests];
    B --> C[macos-latest];
    B --> D[macos-10.15];
    B --> E[ubuntu-latest];
    B --> F[ubuntu-18.04];
    C --> G[make tests];
    D --> G[make tests];
    E --> G[make tests];
    F --> G[make tests];
    G--> H{Ok?};
    H -- Yes --> J[release];
    H -- No --> K[Exit];
    J --> L[release];
    L --> M[version change];
```

## [bats.bash](./bin/bats.bash)

Bats helpers

### Install

````shell
brew install j5pu/tap/shrc
````
