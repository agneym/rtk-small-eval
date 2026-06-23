# rtk evaluation summary: resolved-only token and tool-call view (6 paired instances)

Generated: 2026-06-23

This is the same rtk-on vs rtk-off comparison as `logs/run_evaluation_summary_20260623.md`, but with unresolved paired instances removed. It includes only instances that resolved in **both** arms.

Excluded from this view:

- `astropy__astropy-14182`: unresolved in both arms. This was a large rtk-on token decrease.
- `astropy__astropy-7746`: unresolved in both arms. This was a large rtk-on token increase.

## Headline: resolved-only

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Resolved instances included | 6 / 6 | 6 / 6 | same set |
| Total tokens spent | 2,946,400 | 5,164,961 | +2,218,561 (+75.3%) |
| Total tool/API calls | 213 | 310 | +97 (+45.5%) |
| Median total tokens per instance | 460,795 | 621,778 | +34.9% |
| Mean total tokens per instance | 491,067 | 860,827 | +75.3% |
| Median calls per instance | 36 | 45.5 | +26.4% |
| Mean calls per instance | 35.5 | 51.7 | +45.5% |

Paired-instance direction:

- Token use decreased on **2 / 6** resolved instances and increased on **4 / 6**.
- Tool/API calls decreased on **1 / 6** resolved instances and increased on **5 / 6**.
- Median paired token delta: **+119,870 tokens**.
- Median paired token percentage delta: **+37.6%**.
- Median paired call delta: **+7.5 calls**.
- Median paired call percentage delta: **+23.1%**.

## Per-instance resolved-only results

| instance | run context | tokens off | tokens on | token delta | token delta % | calls off | calls on | call delta |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `astropy__astropy-12907` | Minimax M3 / OpenCode Go | 163,378 | 157,076 | -6,302 | -3.9% | 19 | 20 | +1 |
| `astropy__astropy-14995` | Minimax M3 / OpenCode Go | 623,671 | 2,567,739 | +1,944,068 | +311.7% | 40 | 110 | +70 |
| `astropy__astropy-6938` | Minimax M3 / OpenCode Go | 596,072 | 683,190 | +87,118 | +14.6% | 51 | 59 | +8 |
| `django__django-10914` | DeepSeek V4 Flash / DeepSeek API | 251,603 | 404,225 | +152,622 | +60.7% | 23 | 30 | +7 |
| `django__django-10924` | DeepSeek V4 Flash / DeepSeek API | 986,158 | 792,366 | -193,792 | -19.7% | 48 | 46 | -2 |
| `django__django-11001` | DeepSeek V4 Flash / DeepSeek API | 325,518 | 560,365 | +234,847 | +72.1% | 32 | 45 | +13 |

## Secondary run-context split

| run context | resolved pairs | total tokens off → on | total calls off → on | median tokens off → on | median calls off → on |
|---|---:|---:|---:|---:|---:|
| Minimax M3 / OpenCode Go | 3 | 1,383,121 → 3,408,005 (+146.4%) | 110 → 189 (+71.8%) | 596,072 → 683,190 | 40 → 59 |
| DeepSeek V4 Flash / DeepSeek API | 3 | 1,563,279 → 1,756,956 (+12.4%) | 103 → 121 (+17.5%) | 325,518 → 560,365 | 32 → 45 |

## Interpretation

Removing unresolved instances makes the rtk-on token picture **worse**, not better: the all-8 summary showed +35.5% total tokens, while the resolved-only view shows **+75.3% total tokens**.

The reason is that one of the unresolved instances, `astropy__astropy-14182`, was the largest rtk-on token reduction in the whole set (-1.43M tokens). Removing it also removes `astropy__astropy-7746`, the largest DeepSeek rtk-on regression, but the net effect of excluding both unresolved cases is still a larger resolved-only token increase.

Resolution itself is controlled in this view by construction: all 6 included instances resolved in both arms. So the measured effect here is purely trajectory cost among successful runs: rtk-on used more tokens and more tool/API calls on this resolved-only subset.
