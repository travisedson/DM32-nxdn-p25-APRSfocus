# DM32-nxdn-p25-APRSfocus

A personal fork of [donttellmeimcute/DM32-nxdn-p25](https://github.com/donttellmeimcute/DM32-nxdn-p25) for one
Baofeng DM-32UV. Kept public as a log; not offered upstream. Changes are patches in `integration/current/`, applied
after upstream's own by `tools/build_current.py`; every push to `main` builds a release here.

## Changes

| Patch | What | On the radio |
|---|---|---|
| `aprs-dual-focus.patch` | Dual watch with one side on the APRS frequency: that side listens 3x as long, holds while a packet comes in (HDLC flag detect, even below squelch, max 2.5 s), and stays ~3 s after a packet for a digipeater's copy. Tests in `aprsTest` / `aprsRadioTest`. | Works: packets decoded on the watched side (heard via Fremont Peak). Voice on the other side is missed more often. |
| `dual-back-ab.patch` | Dual watch on Home: **Back** switches A/B (the DM-32UV has no A/B key); **holding Back** stops the watch. From a menu, held Back still only goes Home. | Works. |
| `dual-arrows-zone.patch` | Dual watch: **Left / Right** (P1 / P2) step the selected channel's zone, as they do on the normal Home, in place of selecting A / B (Back does that now). | Works. |
| `aprs-mute.patch` | APRS page, **Mute APRS audio** (second to last row): the speaker stays off on the APRS frequency in FM; decoding, Stations heard and the green LED go on; holding Monitor plays it. Stored in settings bit `SETTINGS_APRS2_MUTE` (0x40 of `aprs_flags2`, unused upstream at `845f9ad5`). Tests in `aprsRadioTest`; APRS page tests in `uiFlowTest` take one more Up. | Works: packets decoded with the speaker silent on B while A brought up a GMRS repeater and its ID was heard. |
| `aprs-rx-release.patch` | Bug fix (upstream behavior): tuning off 144.390 onto a P25/NXDN/YSF channel, APRS receive still held the HR_C7000's FM audio interrupt, so the digital engine refused to start (`dmr_glue.c` `air_take`) and nothing retried it until the next retune. PTT then failed with "NO TX / Release PTT, try again", in dual watch and in single-channel mode after it, until a power cycle. APRS now releases the audio before the radio retunes. Test in `aprsRadioTest`. | Works: P25 PTT while the APRS side receives, and in single-channel mode after dual watch. |

## Upstream backport

**RadioFoundry #660 (`845f9ad5`, "Audio: prevent HR_C7000 speaker FIFO starvation")**, for choppy, distorted P25
receive audio: `p25-audio-fifo.patch`, last in the chain (only the host-test Makefile hunk redone by hand). It was
dropped once (`9a0e33e`) on suspicion of a P25 "NO TX" fault that turned out to be the APRS/engine start bug fixed by
`aprs-rx-release.patch`, and restored after that fix. Drop it once upstream moves its RadioFoundry pin past
`845f9ad5`.

## Updating

**Sync fork** on GitHub, then check the build. If upstream moves its RadioFoundry pin past `845f9ad5`, remove
`p25-audio-fifo.patch`.
