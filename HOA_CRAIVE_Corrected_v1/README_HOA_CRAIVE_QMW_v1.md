# QMW Bloch Harmonics v8 → analog snake → CRAIVE HOA test v1

This test bundle is for two computers connected by a 16-channel analog snake.

## Signal path

Computer 1 runs the unmodified QMW Bloch Harmonics v8 patch:

`QMW HOA3 ACN 0–15 / SN3D → dac~ 1 ... 16 → 16 analog outputs`

Computer 2 runs:

`16 analog inputs → HOA gain → spat5.hoa.rotate~ → spat5.hoa.decoder~ → CRAIVE speaker feeds`

Open `HOA_test_CRAIVE_QMW_v8_analog_receiver_v1.maxpat` on computer 2 and keep `qmw_craive_hoa134_layout_v1.maxpat` in the same folder.

For remote rotation, open `QMW_CRAIVE_HOA_rotation_sender_v1.maxpat` on computer 1.

## Required channel mapping

The receiver preserves the input selection from the supplied `HOA_test.maxpat`:

| QMW output / ACN | Receiver ADC |
|---:|---:|
| 1–8 / ACN 0–7 | 17–24 |
| 9–16 / ACN 8–15 | 33–40 |

Every analog cable must preserve this order. Any swapped channel changes the spherical-harmonic basis and corrupts the decoded field.

The receiver deliberately removes `spat5.hoa.encoder~`. QMW Bloch Harmonics v8 has already encoded the audio as third-order 3D HOA with ACN ordering and SN3D normalization. Encoding it a second time is incorrect.

## Decoder and output scope

The receiver uses:

`spat5.hoa.decoder~ @order 3 @dimension 3D @outputs 134 @mc 1`

The layout loader supplies the verified CRAIVE perimeter coordinates for channels 1–128 and six documented ceiling coordinates for channels 129–134. Energy-preserving decoding and power compensation are enabled.

The final `mc.dac~` exposes hardware slots 1–142. Only decoded loudspeaker feeds 1–134 contain signal. Slots 135–142 remain silent rather than receiving invented speaker coordinates.

This is an experimental all-array HOA decoder assembled from the geometry available in the workspace. CRAIVE documentation describes the six ceiling HOA speakers as working with selected perimeter speakers, but the exact facility-approved subset was not present. Keep the room level low until the routing is verified with lab staff.

## First room test

1. On computer 1, leave the original QMW v8 `dac~ 1 ... 16` output intact.
2. On computer 2, select the interface that receives all 16 snake channels.
3. Confirm the Max input mapping really exposes the snake as inputs 17–24 and 33–40.
4. Disable phantom power on the receiving inputs and use matched line-level gain.
5. Open the corrected receiver and confirm that the Spat decoder and layout abstraction are not red or missing.
6. Click “reload CRAIVE decoder geometry.”
7. Select the CRAIVE output device and confirm it exposes at least 134 outputs.
8. Begin with the room gain low. The receiver includes a fixed `mc.*~ 0.1` safety trim, approximately −20 dB.
9. Test the 16 snake lines individually before testing the complete HOA stream.

Do not connect the 16 incoming HOA components directly to the room DAC. They are spherical-harmonic coefficients, not individual loudspeaker feeds.

## Experimental three-ring 30-speaker receiver

`HOA_test_CRAIVE_QMW_v8_three_ring30_experimental_v1.maxpat` is a separate test configuration. It leaves the 134-speaker receiver unchanged.

Its decoder order and hardware routing are:

- center 16: `4 8 12 16 20 23 28 33 37 42 46 51 55 58 63 1`
- lower 8: `129 130 131 132 133 134 135 136`
- upper 6: `137 138 139 140 141 142`

The center ring uses the supplied XY coordinates exactly. Its supplied `z = 1.30 m` is treated as the listener-height plane, so the decoder-relative center-ring Z coordinate is zero.

The lower and upper coordinates are provisional because their measured coordinates were unavailable. Both use a 5.5 m radius: the lower eight are spaced every 45 degrees at 1 m below the listener plane, and the upper six are spaced every 60 degrees at 1 m above it. Confirm outputs 129–142 and replace these estimated elevations with measured coordinates before treating this as a final room decoder.

Test every hardware output individually at very low level before decoding program material.

## Rotation OSC over the shared network

All rotation control is generated on computer 1. The CRAIVE receiver only listens and applies valid messages to `spat5.hoa.rotate~`.

The dedicated path and port are:

`UDP 7475 · /qmw/craive/hoa/ypr <yaw> <pitch> <roll>`

The receiver also accepts these paths:

- `/qmw/craive/hoa/yaw <degrees>`
- `/qmw/craive/hoa/pitch <degrees>`
- `/qmw/craive/hoa/roll <degrees>`
- `/qmw/craive/hoa/quat <w> <x> <y> <z>`

Before using the sender, replace `127.0.0.1` in its `spat5.osc.udpsend` object with the CRAIVE computer's shared-network IPv4 address. The CRAIVE computer may show a firewall prompt the first time Max listens on UDP 7475; allow incoming traffic for Max.

The sender refreshes the current yaw/pitch/roll state at 10 Hz. This is deliberately low-bandwidth, but it means one dropped UDP packet is corrected by the next refresh and the current orientation returns automatically after a brief interruption.

If the network stops:

- the 16-channel analog HOA audio continues uninterrupted;
- the rotator holds its last valid orientation;
- the receiver's OSC-status toggle goes dark after one second;
- the local yaw, pitch and roll controls in the receiver remain available as a non-network fallback.

No clock synchronization is required for this control stream. Avoid Wi-Fi if possible; use the shared wired network, and do not send rotation updates faster than the supplied sender.
