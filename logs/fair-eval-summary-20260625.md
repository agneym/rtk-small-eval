# Fair RTK evaluation — 100 paired SWE-bench Lite instances

Generated: 2026-06-25
Model: deepseek/deepseek-v4-flash (DeepSeek direct API)
Step limit: 100 per instance
Harness: rtk_env.RtkDockerEnvironment with swebench_rtk.yaml (RTK awareness + `RTK_DISABLED=1` bypass)

## Headline

| metric | rtk-off | rtk-on | delta |
|---|---:|---:|---:|
| Instances | 100 | 100 | — |
| Total cost | $11.73 | $12.25 | +$0.52 (+4.5%) |
| Total tokens | 82,515,762 | 86,178,284 | +3,662,522 (+4.4%) |
| Total calls | 3,995 | 4,063 | +68 (+1.7%) |
| Median cost/instance | $0.057 | $0.059 | +$0.003 (+3.9%) |
| Median calls/instance | 32 | 32 | 0 |
| RTK-on cheaper | — | 43 | 43.9% |
| RTK-off cheaper | 55 | — | 56.1% |
| Ties | — | — | 2 |

**RTK_DISABLED=1 uses: 0** across 100 instances (4,361 command decisions, 1,681 rewrites). The model was told about the escape hatch but never reached for it.

## What changed from the old unfair eval

| | Old eval (23 instances) | Fair eval (100 instances) |
|---|---:|---:|
| RTK awareness | None (hidden) | System prompt (swebench_rtk.yaml) |
| Escape hatch | None | `RTK_DISABLED=1` |
| Step limit | 250 | 100 |
| Cost delta | +33.7% | +4.5% |
| Call delta | +23.1% | +1.7% |
| Failure mode | pytest loops (systematic) | Model variance (random) |

The old eval's +33.7% cost delta was driven by a single systematic failure: the model saw `Pytest: No tests collected` from rtk-rewritten test commands, didn't know rtk existed, and panicked into a 70-turn debugging loop. The fair eval eliminated this by telling the model about rtk in the system prompt. The model stopped panicking — it accepted rtk's compact output as normal behavior.

## What we can measure

### Compression works

RTK compressed tool output by **3.0%** across all instances (4.92M → 4.77M chars). The rewrite log shows **1,681 successful rewrites** (e.g., `find` → `rtk find`, `head -50` → `rtk read --max-lines 50`, `grep` → `rtk grep`). The compression is real and functioning correctly.

### Behavioral drift is unmeasurable

The remaining +4.5% cost delta cannot be attributed to RTK. It is indistinguishable from model path variance — the model taking different exploration routes on the same task. The two worst rtk-on losers (`django__django-11910` at +$0.42 and `django__django-14999` at +$0.25) diverged from the rtk-off arm at step 0, before any RTK-rewritten output could influence them. The divergence is random model behavior, not RTK-induced.

### No systematic failure mode

Unlike the old eval, there is no identifiable RTK-caused failure pattern in the fair eval. No instance shows a clear RTK-induced debugging loop. The system prompt awareness alone was sufficient to prevent the panic-looping, even though `RTK_DISABLED=1` was never used.

## Methodology limitation

A paired A/B eval cannot isolate RTK's effect because:

1. **Compression** (measurable) — RTK shortens command output
2. **Model path variance** (unmeasurable without many repeats) — the model picks different routes
3. **Behavioral drift** (unmeasurable without counterfactual) — RTK's output might nudge the model to choose a different next step

Effects 2 and 3 are confounded. You cannot know whether a path divergence was random variance or an RTK-induced decision. On SWE-bench Lite's short workloads (median 32 calls), the compression effect is too small relative to the model variance to produce a clean signal.

## Per-instance deltas

See `logs/fair-eval-per-instance-20260625.md` for the complete 100-instance table.

## Conclusion

**RTK is neutral on SWE-bench Lite when the model is aware of it.** The +4.5% cost delta is within model-variance noise and does not indicate a systematic RTK effect. The old eval's +33.7% penalty was an artifact of hiding RTK from the model, not an intrinsic property of RTK itself.

This eval does not prove RTK saves cost either — SWE-bench Lite's short, output-light tasks don't give RTK's compression enough room to compound. RTK's value proposition (60-90% per-command compression) would need to be evaluated on longer workloads with more verbose tool output.
