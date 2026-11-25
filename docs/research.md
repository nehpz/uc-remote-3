# Research and first decisions

## Boundaries

- [Remote 3](https://www.unfoldedcircle.com/remote-3) and [Dock 3](https://www.unfoldedcircle.com/dock-3) are separate products. Remote 3 runs the configuration and integration stack; the dock provides power and additional control connectivity. An integration cannot by itself replace the configurator or fix Remote OS/Dock firmware.
- The [Core API documentation](https://unfoldedcircle.github.io/core-api/) includes both the Core REST/WebSocket interfaces and the WebSocket **Integration API**. Drivers expose entities and handle subscription/command/setup traffic; the remote is the WebSocket client. Drivers need not be firmware changes.
- External drivers run on another trusted machine and can be iterated without uploading to the remote. [Custom on-remote installation](https://unfoldedcircle.github.io/core-api/integration-driver/driver-installation.html) is still described as a developer preview. Treat installability and operational stability as separate from archive validity.
- Official runtime options include [the Python wrapper](https://github.com/unfoldedcircle/integration-python-library) and [TypeScript example](https://github.com/unfoldedcircle/integration-ts-example). The [Python release](https://pypi.org/project/ucapi/0.7.0/) requires Python 3.11+. The wrapper does not support secure WebSocket or token-based authentication. Start with loopback, and opt into trusted LAN-only exposure when needed.

## Apple TV as a diagnostic example

Start with the [Apple TV 4K volume diagnostic runbook](apple-tv-volume.md) for investigating rocker and slider behavior.

The [official Apple TV driver](https://github.com/unfoldedcircle/integration-appletv) is firmware-bundled and uses `pyatv`. Upstream documents how to run a separate external development instance with a changed ID, and warns against installing the built-in driver as a custom driver. Its [v0.26.1 integration release](https://github.com/unfoldedcircle/integration-appletv/releases/tag/v0.26.1) has a discovery fix for Apple TV 4K (4th generation); that tag is distinct from the Remote OS version and does not establish what's installed on a given remote. Record Apple TV generation/tvOS, Remote OS version/channel, and exact failure stage (discovery, PIN/pairing, state, command, or wake/reconnect) before deciding whether to extend the upstream driver or work on a different integration.

## First choices

1. Pick the first device/workflow and what a successful button press or activity should do.
2. Prefer an on-remote release so day-to-day control has no separate host dependency. Develop on loopback first, then validate the vendor archive, target runtime and actual Remote 3 behavior. Use an always-on trusted LAN host only if device runtime or sandbox limits prevent a reliable embedded release.
3. Start on the installed firmware channel. Compare release notes with the observed failure; don't adopt beta firmware merely to test a driver. Do not upload to a daily-use remote until loopback and external validation are complete, a physical test is approved, and rollback is understood.

Version evidence: check [official Remote OS changelog](https://www.unfoldedcircle.com/changelog), the associated integration release, and installed versions separately. An upstream tag, downloaded artifact, and installed build are different facts. The [Dock 3 firmware releases](https://github.com/unfoldedcircle/ucd3-firmware/releases) are a separate version stream.
