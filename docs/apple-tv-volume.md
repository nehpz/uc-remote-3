# Apple TV 4K volume: diagnostic runbook

**Diagnostic scenario.** After successful pairing, check reports of a Remote 3 volume rocker or touch slider reverting to the previous level or appearing to change without input. Separate physical volume changes from display-only changes. This runbook does not claim reproduction or compatibility for any hardware configuration.

## What the upstream code does

- [v0.26.1 media-player commands](https://github.com/unfoldedcircle/integration-appletv/blob/v0.26.1/intg-appletv/media_player.py#L205-L229) dispatch relative up/down separately from absolute set. This describes what happens *if* a control targets that entity, not how a particular activity is mapped.
- [v0.26.1 Apple TV transport](https://github.com/unfoldedcircle/integration-appletv/blob/v0.26.1/intg-appletv/tv.py#L1421-L1476) sends relative requests through the pyatv audio interface. Absolute set requires its MRP audio route and may write to multiple outputs when Global Volume is enabled. A command result is not proof of an audible change or fresh state.
- [v0.26.1 volume feedback](https://github.com/unfoldedcircle/integration-appletv/blob/v0.26.1/intg-appletv/tv.py#L517-L559) forwards volume events and can calculate an aggregate from output-device levels with Global Volume on. [pyatv notes](https://pyatv.dev/development/listeners/) that volume update availability depends on the audio connection. A stale echo, another endpoint, or a new input event are hypotheses, not established causes. The [v0.26.1 release notes](https://github.com/unfoldedcircle/integration-appletv/releases/tag/v0.26.1) do not identify a fix for this symptom.

**Check the output route before treating slider behavior as a bug.** The [Unfolded Circle changelog](https://github.com/unfoldedcircle/integration-appletv/blob/v0.26.1/CHANGELOG.md#L155-L160) documents absolute/global volume for connected outputs such as HomePod, not HDMI. [Home Assistant's pyatv-backed integration](https://www.home-assistant.io/integrations/apple_tv/#setting-volume-doesnt-work-on-my-apple-tv) similarly distinguishes relative HDMI-CEC control from absolute volume; the Siri Remote's direct IR commands don't take the Apple TV LAN path. For an HDMI-connected TV, receiver, or soundbar, check whether the rocker and slider actually target the Apple TV or the equipment that controls volume. Unfolded Circle's [activity guide](https://support.unfoldedcircle.com/hc/en-us/articles/13269248303516-How-to-create-an-activity) documents direct mapping to the volume-controlling device; a slider should only be expected to set a level if its target supports absolute volume. This is a diagnostic distinction, not authorization to change the activity.

## Capture before changing anything

Record Remote OS build/channel, bundled Apple TV integration version if exposed (otherwise unknown), tvOS build, active activity and source, exact rocker and slider entity/command mappings, Global Volume setting if visible, and active audio output(s). Distinguish HDMI/CEC, TV speakers, receiver/soundbar, and HomePod/AirPlay as applicable. Keep the network connection, source/program, output route, and a safe starting level fixed. Leave normal activities and device settings unchanged during baseline capture.

For each trial, record elapsed time, control touched (or none), activity/entity, requested action/value, any driver response and state update timestamp, Remote 3 display, **physical endpoint level (or audible change if no endpoint reading)**, and output route. Mark unavailable evidence as unknown rather than inferring it. Compare baseline to the same input sequence and endpoint after any one change. Use these evidence cuts:

| Isolated trial | Record and compare |
| --- | --- |
| Remote flat and untouched for 60 seconds, slider page visible; repeat with it off screen | Did any UI, command, state, or actual output change? Record wake, output changes, and any deliberate action by another controller separately. |
| One rocker up, wait five seconds, then one down | Watch requested command versus response, displayed state and endpoint level. Repeat at a safe midrange to avoid conflating a limit with a fault. |
| Touch slider once, then drag and release in another trial | Record whether a command is sent during drag/release, whether the UI snaps back, and whether physical output follows or stays put. Wait at least five seconds after each. |
| Siri Remote or verified native output control, no Remote 3 input | Determine whether the endpoint is stable under native control and whether Remote 3 reflects the change without sending a new command. |

If diagnostics need more visibility, a **separately approved** external v0.26.1 test driver can provide timestamped logs at the Integration API/pyatv boundary. Use a unique ID and temporary entity or activity, do not replace the bundled driver, and keep only one controller writing volume during a trial. Run the same matrix on the same path before comparing changes. A differing result on an external driver is evidence, not proof of the root cause, since execution location also changes. Use synthetic endpoint names and strip pairing keys, device identifiers, addresses, and raw config from shared traces.

## Offline regression tests for a future change

- Verify one relative step command per intended tap and no commands on idle, UI redraw, or state update. Verify the absolute set request on deliberate slider input; define coalescing separately for drags.
- Test command accepted vs transport timeout/error vs physical/state confirmation, including no notification and a successful command with delayed confirmation.
- Replay prior level → request new level → stale prior-level echo → confirmed new level, including duplicate/out-of-order echoes and two rapid requests. Do not let a known stale echo overwrite a confirmed newer state or trigger a new command. After the pending window, a genuine native/external change should still appear; don't blanket-ignore differing values.
- Replay output switches and multi-output aggregation. Verify that events from the previous endpoint are not mistaken for the active output and that unsupported absolute set is surfaced without pretending the level changed.

**Pass:** both controls reliably change the intended output once per intended action, confirmed display converges with that output (or with an explicitly defined group level), and idle does not generate volume commands. Record baseline and candidate pass/fail/not-run separately. No device or settings changes have been made for this runbook.
