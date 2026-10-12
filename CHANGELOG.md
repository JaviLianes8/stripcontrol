# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

- `strip_control` removes C0, DEL and C1 control characters while keeping tab,
  newline and carriage return, with a configurable keep set.
- `has_control` reports whether text holds a control character other than standard
  whitespace.
- `find_control` lists the index and codepoint of each such control character.
