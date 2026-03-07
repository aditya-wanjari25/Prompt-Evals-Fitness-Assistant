# Eval Findings — Fitness AI Prompt

## Overview
Built a prompt evaluation suite for an AI personal fitness trainer.
Tested across 6 scenario categories with 13 test cases and 5 assertion types.

## Prompt Versions

### v1 — Baseline
Simple prompt with basic instructions.
**Score: 100% (38/38)**

### v2 — Structured with guidelines
Added category-specific behavior rules (beginner, advanced, injury, vague, etc.)
**Score: 97% (37/38)** after fixing two assertion bugs caught during v2 eval run.

## Failures & What I Learned

### Failure 1 — Advanced question flagged as too long
**Test case:** "I'm training for a powerlifting meet in 8 weeks, how should I peak?"
**Assertion failed:** `concise` (150 word limit)
**Root cause:** Assertion was too strict — detailed advice for complex questions
legitimately requires more words.
**Fix:** Added `concise_extended` (250 words) for advanced category test cases.
**Lesson:** Not every assertion applies equally to every category. Good evals
are context-aware.

### Failure 2 — Clarifying question flagged as not addressing input
**Test case:** "Just make me fit"
**Assertion failed:** `addresses_input` (response under 30 words)
**Root cause:** v2 prompt correctly instructs the model to ask a clarifying
question for vague inputs. The assertion penalized correct behavior.
**Fix:** Updated `addresses_input` to pass if the response contains a
clarifying question, even if short.
**Lesson:** When an assertion fails, the bug is sometimes in the assertion
itself, not the prompt. Diagnosing which one is wrong is a core eval skill.

## Key Takeaways
- Writing good assertions is just as hard as writing good prompts
- Evals caught a regression in v2 before it would have shipped
- Keyword-based assertions are fast but miss nuance — LLM-as-judge is next