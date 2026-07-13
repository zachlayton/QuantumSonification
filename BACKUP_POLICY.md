# Backup and versioning policy

## Repository scope

The repository root is the complete `QuantumSonification` workspace. This is
intentional: the QMW project depends on shared modules outside its own folder.

## Preserve history

- Never overwrite a committed render family.
- Fork experiments into revisioned sibling directories.
- Commit source and configuration changes before starting a materially new
  experiment family.
- Record parameters and provenance in machine-readable manifests.

## Git LFS

Git LFS stores audio, NumPy state archives, ZIP archives, rendered images,
PDFs, and native 3D documents. Text source, Max patches, GenExpr, JSON,
manifests, Markdown, and OBJ geometry remain ordinary Git content.

Before pushing, verify that `git lfs ls-files` includes every intended large
binary and that ordinary Git contains no unexpectedly large blobs.

## Exclusions

Python caches, macOS metadata, editor state, local environments, downloaded
command-line tools, logs, temporary files, and credential-bearing files are
excluded. Never commit API keys, access tokens, private keys, or `.env` files.

## GitHub

The initial GitHub repository should be private. A public release, if desired,
should be prepared later as a curated repository or tagged release after
licensing, attribution, dependency, and media-rights review.

