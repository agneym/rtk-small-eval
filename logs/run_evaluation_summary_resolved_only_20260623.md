# rtk evaluation summary: resolved-only token and tool-call view (11 paired instances)

Generated: 2026-06-23 21:17:00

This is the same comparison as `logs/run_evaluation_summary_20260623.md`, but with unresolved paired instances removed. It includes only instances that resolved in **both** arms.

Excluded from this view:

- `astropy__astropy-14182`: resolved no → no.
- `astropy__astropy-7746`: resolved no → no.

## Headline: resolved-only

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Resolved instances included | 11 / 11 | 11 / 11 | same set |
| Total tokens spent | 3,457,042 | 6,030,991 | +2,573,949 (+74.5%) |
| Total tool/API calls | 298 | 418 | +120 (+40.3%) |
| Median total tokens per instance | 163,378 | 243,380 | +49.0% |
| Mean total tokens per instance | 314,277 | 548,272 | +74.5% |
| Median calls per instance | 20 | 27 | +35.0% |
| Mean calls per instance | 27.1 | 38.0 | +40.3% |

## Per-instance resolved-only results

| instance | run context | tokens off | tokens on | token delta | token delta % | calls off | calls on | call delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `astropy__astropy-12907` | Minimax M3 / OpenCode Go | 163,378 | 157,076 | -6,302 | -3.9% | 19 | 20 | +1 |
| `astropy__astropy-14995` | Minimax M3 / OpenCode Go | 623,671 | 2,567,739 | +1,944,068 | +311.7% | 40 | 110 | +70 |
| `astropy__astropy-6938` | Minimax M3 / OpenCode Go | 596,072 | 683,190 | +87,118 | +14.6% | 51 | 59 | +8 |
| `django__django-10914` | DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | 251,603 | 404,225 | +152,622 | +60.7% | 23 | 30 | +7 |
| `django__django-10924` | DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | 986,158 | 792,366 | -193,792 | -19.7% | 48 | 46 | -2 |
| `django__django-11001` | DeepSeek V4 Flash / DeepSeek API (slice 5:10 completed pairs) | 325,518 | 560,365 | +234,847 | +72.1% | 32 | 45 | +13 |
| `django__django-11039` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | 95,013 | 212,805 | +117,792 | +124.0% | 17 | 24 | +7 |
| `django__django-11049` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | 113,053 | 210,482 | +97,429 | +86.2% | 19 | 25 | +6 |
| `django__django-11099` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | 52,555 | 43,913 | -8,642 | -16.4% | 13 | 12 | -1 |
| `django__django-11133` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | 116,593 | 243,380 | +126,787 | +108.7% | 16 | 27 | +11 |
| `django__django-11179` | DeepSeek V4 Flash / DeepSeek API (slice 10:15) | 133,428 | 155,450 | +22,022 | +16.5% | 20 | 20 | +0 |

## Interpretation

On the resolved-only set, rtk-on again costs more: **+74.5%** more total tokens and **+40.3%** more calls. The newly added next-5 slice is fully resolved in both arms, so it increases the resolved-only sample from 6 to 11 while preserving the same overall direction.
