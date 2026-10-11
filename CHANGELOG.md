# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

- First release: parse and build the HTTP Via header per RFC 9110, with typed hops,
  an optional protocol name defaulting to HTTP, comment handling, and comma-aware
  splitting that never breaks inside a comment.
