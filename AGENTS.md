# Agent guide

This is a public workspace for Unfolded Circle Remote 3 integrations, not a firmware, web configurator, or Dock 3 replacement.

1. Read README.md and docs/research.md. Check upstream API/SDK and firmware requirements before changing an integration.
2. Give each integration a unique, stable driver ID under the project namespace (never use the reserved `uc_` prefix or copy built-in IDs). Keep the device transport behind an adapter; run it against fakes in tests.
3. Run `make check`. Report the exact commands and distinguish synthetic tests from simulator and physical-device results. Do not claim compatibility from a successful package build.
4. Start external with loopback and discovery disabled. Don't pair, scan the LAN, upload drivers, modify a remote, install firmware, or interact with a physical device as part of ordinary development/CI. Establish a specific hardware test plan first.
5. Treat every tracked file, commit message, Git author email, workflow run, and release artifact as public. Never commit personal names or contact details, private repository or host information, local paths, addresses, identifiers, pairing material, real configuration/logs, or screenshots of private setups. Use synthetic fixtures; review staged files and archive contents before publication.
6. Read docs/release.md before packaging. Never publish from pull requests or infer publication approval. Preserve other workspace changes.
7. Prioritize an on-remote release to avoid requiring a separate uptime dependency. Develop externally with fake/loopback first; an always-on trusted host is a fallback, not a requirement.
8. Use MPL-2.0 for original project source. Retain upstream file notices when adapting source and document dependencies and bundled notices before redistribution. Do not assume another component is licensed under MPL-2.0 or that a trademark is licensed by the software license.
