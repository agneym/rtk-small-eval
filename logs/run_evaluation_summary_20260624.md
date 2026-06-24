# rtk evaluation summary: tokens, tool calls, and resolved status (18 paired instances)

Generated: 2026-06-24

This summary covers all completed paired SWE-bench Lite instances across four slices: 0:5 (MiniMax M3), 5:10 (DeepSeek V4 Flash), 10:15 (DeepSeek V4 Flash), and 15:20 (DeepSeek V4 Flash).

## Headline

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Resolved | 15 / 18 | 15 / 18 | no change |
| Total tokens spent | 9,171,502 | 12,158,250 | +2,986,748 (+32.6%) |
| Total tool/API calls | 573 | 723 | +150 (+26.2%) |
| Median total tokens per instance | 188,142 | 399,808 | +112.5% |
| Mean total tokens per instance | 509,528 | 675,458 | +32.6% |
| Median calls per instance | 23 | 30 | +30.4% |
| Mean calls per instance | 31.8 | 40.2 | +26.2% |

Paired-instance direction:

- Token use decreased on **5 / 18** paired instances and increased on **13 / 18**.
- Tool/API calls decreased on **3 / 18** paired instances, were unchanged on **2 / 18**, and increased on **13 / 18**.

## Per-instance token and call deltas

| instance | run context | resolved off → on | tokens off | tokens on | token delta | token delta % | calls off | calls on | call delta |
|---|---|---|---|---|---|---|---|---|---|
| `astropy__astropy-12907` | MiniMax M3 (slice 0:5) | yes → yes | 163,378 | 157,076 | -6,302 | -3.9% | 19 | 20 | +1 |
| `astropy__astropy-14182` | MiniMax M3 (slice 0:5) | no → no | 2,040,992 | 609,360 | -1,431,632 | -70.1% | 82 | 43 | -39 |
| `astropy__astropy-14995` | MiniMax M3 (slice 0:5) | yes → yes | 623,671 | 2,567,739 | +1,944,068 | +311.7% | 40 | 110 | +70 |
| `astropy__astropy-6938` | MiniMax M3 (slice 0:5) | yes → yes | 596,072 | 683,190 | +87,118 | +14.6% | 51 | 59 | +8 |
| `astropy__astropy-7746` | DeepSeek V4 Flash (slice 5:10) | no → no | 185,426 | 1,237,088 | +1,051,662 | +567.2% | 20 | 56 | +36 |
| `django__django-10914` | DeepSeek V4 Flash (slice 5:10) | yes → yes | 251,603 | 404,225 | +152,622 | +60.7% | 23 | 30 | +7 |
| `django__django-10924` | DeepSeek V4 Flash (slice 5:10) | yes → yes | 986,158 | 792,366 | -193,792 | -19.7% | 48 | 46 | -2 |
| `django__django-11001` | DeepSeek V4 Flash (slice 5:10) | yes → yes | 325,518 | 560,365 | +234,847 | +72.1% | 32 | 45 | +13 |
| `django__django-11039` | DeepSeek V4 Flash (slice 10:15) | yes → yes | 95,013 | 212,805 | +117,792 | +124.0% | 17 | 24 | +7 |
| `django__django-11049` | DeepSeek V4 Flash (slice 10:15) | yes → yes | 113,053 | 210,482 | +97,429 | +86.2% | 19 | 25 | +6 |
| `django__django-11099` | DeepSeek V4 Flash (slice 10:15) | yes → yes | 52,555 | 43,913 | -8,642 | -16.4% | 13 | 12 | -1 |
| `django__django-11133` | DeepSeek V4 Flash (slice 10:15) | yes → yes | 116,593 | 243,380 | +126,787 | +108.7% | 16 | 27 | +11 |
| `django__django-11179` | DeepSeek V4 Flash (slice 10:15) | yes → yes | 133,428 | 155,450 | +22,022 | +16.5% | 20 | 20 | +0 |
| `django__django-11283` | DeepSeek V4 Flash (slice 15:20) | yes → yes | 158,836 | 827,200 | +668,364 | +420.8% | 16 | 43 | +27 |
| `django__django-11422` | DeepSeek V4 Flash (slice 15:20) | yes → yes | 520,638 | 739,211 | +218,573 | +42.0% | 36 | 39 | +3 |
| `django__django-11564` | DeepSeek V4 Flash (slice 15:20) | no → no | 575,578 | 1,423,574 | +847,996 | +147.3% | 31 | 49 | +18 |
| `django__django-11583` | DeepSeek V4 Flash (slice 15:20) | yes → yes | 145,612 | 207,407 | +61,795 | +42.4% | 18 | 21 | +3 |
| `django__django-11620` | DeepSeek V4 Flash (slice 15:20) | yes → yes | 2,088,378 | 1,083,419 | -1,004,959 | -48.1% | 72 | 54 | -18 |

## Run-context split

| run context | pairs | resolution off → on | total tokens off → on | median tokens off → on | total calls off → on | median calls off → on |
|---|---|---:|---:|---:|---:|---:|---:|
| MiniMax M3 (slice 0:5) | 4 | 3/4 → 3/4 | 3,424,113 → 4,017,365 (+17.3%) | 609,872 → 646,275 | 192 → 232 (+20.8%) | 45.5 → 51 |
| DeepSeek V4 Flash (slice 5:10) | 4 | 3/4 → 3/4 | 1,748,705 → 2,994,044 (+71.2%) | 288,560 → 676,366 | 123 → 177 (+43.9%) | 27.5 → 45.5 |
| DeepSeek V4 Flash (slice 10:15) | 5 | 5/5 → 5/5 | 510,642 → 866,030 (+69.6%) | 113,053 → 210,482 | 85 → 108 (+27.1%) | 17 → 24 |
| DeepSeek V4 Flash (slice 15:20) | 5 | 4/5 → 4/5 | 3,488,042 → 4,280,811 (+22.7%) | 520,638 → 827,200 | 173 → 206 (+19.1%) | 31 → 43 |

## Evaluation-log locations

| run context | rtk-off logs | rtk-on logs |
|---|---|---|
| MiniMax M3 (slice 0:5) | `logs/run_evaluation/rtk-off-20260623/anthropic__minimax-m3/sb_result.json` | `logs/run_evaluation/rtk-on-20260623/anthropic__minimax-m3/sb_result.json` |
| DeepSeek V4 Flash (slice 5:10) | `logs/run_evaluation/rtk-off-deepseek-20260623/deepseek__deepseek-v4-flash/sb_result.json` | `logs/run_evaluation/rtk-on-deepseek-20260623/deepseek__deepseek-v4-flash/sb_result.json` |
| DeepSeek V4 Flash (slice 10:15) | `logs/run_evaluation/rtk-off-deepseek-slice10-15-20260623/deepseek__deepseek-v4-flash/sb_result.json` | `logs/run_evaluation/rtk-on-deepseek-slice10-15-20260623/deepseek__deepseek-v4-flash/sb_result.json` |
| DeepSeek V4 Flash (slice 15:20) | `logs/run_evaluation/rtk-off-deepseek-slice15-20-20260624/sb_result.json` | `logs/run_evaluation/rtk-on-deepseek-slice15-20-20260624/sb_result.json` |

## Exclusions

- `astropy__astropy-14365`: excluded from the MiniMax paired set because the earlier rtk-off run hung.
- `django__django-11019`: excluded from the DeepSeek slice 5:10 paired set because the initial rtk-off/rtk-on runs did not complete a paired trajectory/prediction for that instance.

## Read-out

Across 18 paired instances, rtk does not change the resolved count (both arms: 15/18). It increases total token spend by **+32.6%** and total tool/API calls by **+26.2%**. All four slices show token/call inflation under rtk-on, with the strongest effects in the DeepSeek V4 Flash slices.
