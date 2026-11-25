# Adding a driver

Put independently deployable integrations in `integrations/<slug>/`. Give each a README, driver metadata, versioned dependency lock, entry point, device adapter, synthetic fixtures, and tests. Document the supported device models, entity IDs/features, setup and cleanup, and exact tested firmware/Core API versions. Hook tests into the root check only when they run without external devices or secrets.

For a Python starting point, inspect [the vendor's official examples](https://github.com/unfoldedcircle/integration-python-library/tree/main/examples) and use `ucapi==0.7.0` with Python 3.11 as the initial candidate. For TypeScript, inspect the [official example](https://github.com/unfoldedcircle/integration-ts-example). The first integration decides which runtime gets committed; the repo tools do not force it.
