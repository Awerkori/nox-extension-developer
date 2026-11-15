# Changelog

## 1.0.1

- Expand bilingual dependency and Android SDK guidance, add practical examples, and clarify Windows/WSL limitations.
- Document verified OpenCode discovery after installation from the public repository.

## 1.0.0

- Added an Agent Skills workflow for Keiyoushi, Yuzono, and LNReader, with on-demand official references pinned to upstream commits.
- Added integrity-checked snapshots, offline fallback, corruption quarantine, and serialized updates.
- Added scoped API comparison with conservative heuristics and documented uncertainty.
- Added local symlink installation and deterministic candidate packaging.
- Added regression tests and documented security, compatibility, licensing, and validation limits.
- Treat added API declarations as indeterminate; adding an interface method can break implementers.
- Read package inputs without following symlinks and publish complete ZIPs without replacing an existing file.
- Clarified natural-language examples, synthetic-test limits, and the owner’s licensing decision.
- Treat unknown or nonnumeric version identifiers as indeterminate in scoped API comparisons.
- Require a known-positive search check and clarify site inspection, dependency reuse, and resuming interrupted work.
- Include both language guides, prompts, and visual assets in the distribution ZIP.
- Install under the canonical skill name even when the source directory was renamed.

Released under AGPL-3.0-only. Third-party projects retain their own licenses; see `ATRIBUICOES.md`.
