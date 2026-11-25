# Development playbook

## Feedback loop

1. Specify one entity and the device action it should trigger. Keep the remote protocol handler separate from the device adapter.
2. Run `make check` and driver tests with fake transport, fixed state, synthetic IDs and no network. Cover setup success and abort; connect/disconnect; subscription; updates and reconnect; supported/unsupported commands; timeout/failure behavior; and redaction. For media players, distinguish standby, unavailable, and idle.
3. Add a loopback contract test using the published [Integration API schema](https://github.com/unfoldedcircle/core-api/tree/main/integration-api). Check driver metadata, entity listing, subscribe and state events, a command response, and disconnect/reconnect. Confirm expected result codes and do not use a real device adapter by default.
4. Optionally run the [official Core Simulator](https://github.com/unfoldedcircle/core-simulator) as a separate local prerequisite, not in the baseline CI. Check the [official Docker notes](https://github.com/unfoldedcircle/core-simulator/tree/main/docker): the documented image is amd64, bridged Docker networking may require manual registration because mDNS discovery is unavailable, and validation of an uploaded custom archive does not demonstrate that it can run. Record the simulator tag and distinguish its coverage from the real remote UI and network stack.

## Bring-up and hardware smoke test

For Python, start with `UC_INTEGRATION_INTERFACE=127.0.0.1`, `UC_DISABLE_MDNS_PUBLISH=true`, a free local port in `UC_INTEGRATION_HTTP_PORT`, and a disposable project-private config directory in `UC_CONFIG_HOME`. Use a fake adapter. Start production-like LAN exposure only for a planned physical test; bind the specific trusted LAN interface, use manual host:port when practical, and don't forward the port or expose it to guest/public networks. If relevant, verify mDNS separately from IP reachability.

Before changing the remote, record firmware/Core API, host, target model and OS, driver version, and current settings needed to restore the prior setup. Keep secrets and network identifiers in a private test record. Add an external test driver with a unique ID, leave built-ins in place, and use a temporary activity/page instead of editing a daily-use one.

Smoke-test add/setup; visible entities; read state; one safe and observable command; sleep/wake and reconnect; incorrect/unavailable device handling; and removing the temporary driver/activity. Record each as passed, failed, or not run. Never switch firmware or wipe existing configuration as a routine smoke-test step.
