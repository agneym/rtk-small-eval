# rtk evaluation summary: resolved-only token and call comparison (15 paired instances)

Generated: 2026-06-24

This summary covers only the 15 instances that resolved in **both** the rtk-off and rtk-on arms. Three instances that did not resolve in either arm — `astropy__astropy-14182`, `astropy__astropy-7746`, `django__django-11564` — are excluded.

## Headline

| metric | rtk-off | rtk-on | delta |
|---:|---:|---:|---:|
| Resolved | 15 / 15 | 15 / 15 | — |
| Total tokens spent | 6,370,506 | 8,888,228 | +2,517,722 (+39.5%) |
| Total tool/API calls | 440 | 575 | +135 (+30.7%) |
| Median total tokens per instance | 163,378 | 404,225 | +147.4% |
| Mean total tokens per instance | 424,700 | 592,549 | +39.5% |
| Median calls per instance | 20 | 30 | +50.0% |
| Mean calls per instance | 29.3 | 38.3 | +30.7% |

Paired-instance direction:

- Token use decreased on **4 / 15** paired instances and increased on **11 / 15**.
- Tool/API calls decreased on **3 / 15** paired instances, were unchanged on **1 / 15**, and increased on **11 / 15**.

## Per-instance token and call deltas

| instance | run context | tokens off | tokens on | token delta | token delta % | calls off | calls on | call delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `astropy__astropy-12907` | MiniMax M3 (slice 0:5) | 163,378 | 157,076 | -6,302 | -3.9% | 19 | 20 | +1 |
| `astropy__astropy-14995` | MiniMax M3 (slice 0:5) | 623,671 | 2,567,739 | +1,944,068 | +311.7% | 40 | 110 | +70 |
| `astropy__astropy-6938` | MiniMax M3 (slice 0:5) | 596,072 | 683,190 | +87,118 | +14.6% | 51 | 59 | +8 |
| `django__django-10914` | DeepSeek V4 Flash (slice 5:10) | 251,603 | 404,225 | +152,622 | +60.7% | 23 | 30 | +7 |
| `django__django-10924` | DeepSeek V4 Flash (slice 5:10) | 986,158 | 792,366 | -193,792 | -19.7% | 48 | 46 | -2 |
| `django__django-11001` | DeepSeek V4 Flash (slice 5:10) | 325,518 | 560,365 | +234,847 | +72.1% | 32 | 45 | +13 |
| `django__django-11039` | DeepSeek V4 Flash (slice 10:15) | 95,013 | 212,805 | +117,792 | +124.0% | 17 | 24 | +7 |
| `django__django-11049` | DeepSeek V4 Flash (slice 10:15) | 113,053 | 210,482 | +97,429 | +86.2% | 19 | 25 | +6 |
| `django__django-11099` | DeepSeek V4 Flash (slice 10:15) | 52,555 | 43,913 | -8,642 | -16.4% | 13 | 12 | -1 |
| `django__django-11133` | DeepSeek V4 Flash (slice 10:15) | 116,593 | 243,380 | +126,787 | +108.7% | 16 | 27 | +11 |
| `django__django-11179` | DeepSeek V4 Flash (slice 10:15) | 133,428 | 155,450 | +22,022 | +16.5% | 20 | 20 | +0 |
| `django__django-11283` | DeepSeek V4 Flash (slice 15:20) | 158,836 | 827,200 | +668,364 | +420.8% | 16 | 43 | +27 |
| `django__django-11422` | DeepSeek V4 Flash (slice 15:20) | 520,638 | 739,211 | +218,573 | +42.0% | 36 | 39 | +3 |
| `django__django-11583` | DeepSeek V4 Flash (slice 15:20) | 145,612 | 207,407 | +61,795 | +42.4% | 18 | 21 | +3 |
| `django__django-11620` | DeepSeek V4 Flash (slice 15:20) | 2,088,378 | 1,083,419 | -1,004,959 | -48.1% | 72 | 54 | -18 |

## Run-context split

| run context | pairs | total tokens off → on | median tokens off → on | total calls off → on | median calls off → on |
|---:|---:|---:|---:|---:|---:|
| MiniMax M3 (slice 0:5) | 3 | 1,383,121 → 3,408,005 (+146.4%) | 596,072 → 683,190 | 110 → 189 (+71.8%) | 40 → 59 |
| DeepSeek V4 Flash (slice 5:10) | 3 | 1,563,279 → 1,756,956 (+12.4%) | 325,518 → 560,365 | 103 → 121 (+17.5%) | 32 → 45 |
| DeepSeek V4 Flash (slice 10:15) | 5 | 510,642 → 866,030 (+69.6%) | 113,053 → 210,482 | 85 → 108 (+27.1%) | 17 → 24 |
| DeepSeek V4 Flash (slice 15:20) | 4 | 2,913,464 → 2,857,237 (-1.9%) | 339,637 → 473,309 | 142 → 157 (+10.6%) | 27 → 31 |

## Excluded instances

| instance | reason |
|---|---|
| `astropy__astropy-14182` | Unresolved in both arms (no → no) |
| `astropy__astropy-7746` | Unresolved in both arms (no → no) |
| `django__django-11564` | Unresolved in both arms (no → no) |
| `astropy__astropy-14365` | Excluded entirely: rtk-off run hung, no paired trajectory |
| `django__django-11019` | Excluded entirely: incomplete paired trajectory |

## Read-out

Across 15 instances that resolved in both arms, rtk-on used **+39.5% more tokens** and **+30.7% more calls**. The resolved-only view is more extreme than the all-instances view (+32.6% / +26.2%) because the unresolved instances happened to show larger token decreases or smaller increases.
