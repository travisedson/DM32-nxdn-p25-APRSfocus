# DM32-nxdn-p25-APRSfocus

A personal fork of [donttellmeimcute/DM32-nxdn-p25](https://github.com/donttellmeimcute/DM32-nxdn-p25) for one
Baofeng DM-32UV. Kept public as a log; not offered upstream. Changes are patches in `integration/current/`, applied
after upstream's own by `tools/build_current.py`; every push to `main` builds a release here.

## Changes

| Patch | What | On the radio |
|---|---|---|
| `aprs-dual-focus.patch` | Dual watch with one side on the APRS frequency: that side listens 3x as long, holds while a packet comes in (HDLC flag detect, even below squelch, max 2.5 s), and stays ~3 s after a packet for a digipeater's copy. Tests in `aprsTest` / `aprsRadioTest`. | Works: packets decoded on the watched side (heard via Fremont Peak). Voice on the other side is missed more often. |
| `dual-back-ab.patch` | Dual watch on Home: **Back** switches A/B (the DM-32UV has no A/B key); **holding Back** stops the watch. From a menu, held Back still only goes Home. | Works. |

## Tried and dropped

**RadioFoundry #660 (`845f9ad5`, "Audio: prevent HR_C7000 speaker FIFO starvation")**, backported for choppy,
distorted P25 receive audio. It applied cleanly and passed the host tests, but on the radio PTT on a P25 channel
while it was receiving anything, noise included, was refused ("NO TX", "Release PTT, try again"), in dual watch and
single-channel mode. Builds without it transmit. Likely an interaction between #660's timer-driven speaker FIFO and
this fork's own changes to the HR_C7000 audio/air glue (`base.patch`); not pinned down. Removed in `9a0e33e`.

## Updating

**Sync fork** on GitHub, then check the build. If upstream moves its RadioFoundry pin past `845f9ad5`, retest P25
PTT while receiving.
