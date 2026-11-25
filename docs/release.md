# Local release preparation

The GitHub Actions workflow only runs checks. Source publication is separate from packaging, signing, or publishing integration assets. A public version's source tag, dependency lock, archive digest and hardware compatibility record should agree. Do not enable automatic publication without an agreed review and rollback process.

## Develop externally; release on the remote first

1. Use a clean checkout and the pinned per-driver dependencies. Run unit/contract checks and record their versions.
2. Validate externally with a fake adapter and loopback first. Target an on-remote archive for everyday use. If an embedded release fails the runtime or reliability checks, document the blocker before offering a host-specific fallback with startup, persistence, rollback and upgrade instructions.
3. Record actual Remote 3 smoke-test results before making compatibility claims. Keep the upstream bundled driver installed during an external experiment; stop/remove only the experimental driver for rollback.

## On-remote package review

Vendor [archive requirements](https://unfoldedcircle.github.io/core-api/integration-driver/driver-installation.html) are not a device compatibility guarantee. For Node, the vendor documents different runtimes by firmware; Node 22 is a starting point, not a blanket compatibility claim. Stage only deployable files: root `driver.json`, then `bin/driver.js` with production dependencies (confirm the target firmware's Node runtime) **or** a self-contained Linux AArch64 executable at `bin/driver`. A macOS binary is not suitable. Python code needs a bundled runtime for on-remote use. Optional `config/` and `data/` must contain only non-sensitive defaults. Runtime state belongs in the provided config/data paths, not the binary folder. No symlinks, no local env/config/cache, and no real pairing material.

Run `python3 tools/validate_archive.py path/to/driver.tar.gz` on the final archive. This is local preflight only. It checks the subset defined in the tool and emits a SHA-256 digest; it never writes extracted files, uploads, publishes, or executes archive code. It does not check binary architecture, image dimensions, or runtime dependencies. Review the package and record runtime/architecture and smoke results separately. Keep the prior tested package/checksum for rollback. Do not upload built-in driver packages as custom drivers.

## Redistribution review

Retain MPL-2.0 notices on adapted covered files and make their corresponding source available as required when distributing executable forms; include a discoverable source link and license notice in release materials. Record bundled components and their exact versions, licenses, and necessary notices. Review runtime, SDK, application and asset obligations separately before adding a binary release. Compatibility references do not imply product endorsement or grant trademark rights.
