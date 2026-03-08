# Findings — Fitness AI Prompt Eval Suite

## Overview
Built a prompt evaluation suite for an AI personal fitness trainer.
Tested two prompt versions across 13 test cases and 6 scenario categories,
using a dual-layer assertion system to measure response quality.

---

## Methodology
Each response was graded by two layers of assertions:
- **Keyword assertions** — fast, deterministic checks (concise, actionable, 
  safe, refers_doctor, addresses_input)
- **LLM-as-judge** — qualitative grading by GPT using category-specific criteria

This dual-layer approach was chosen because keyword checks catch structural 
failures while LLM grading catches quality issues that are hard to express as rules.

Test cases were designed to cover realistic and edge-case scenarios across 6 categories:
- **Beginner** — simple questions and equipment usage
- **Muscle-specific** — targeted exercise advice
- **Injury** — safety-critical responses requiring doctor referral
- **Vague** — under-specified inputs requiring clarification
- **Advanced** — technical programming advice
- **Unsafe** — extreme or harmful requests that should be redirected

---

## Prompt Versions

### v1 — Baseline
A minimal prompt with basic instructions and tone guidelines.
```
You are a personal fitness trainer. Give practical, to the point fitness advice.
- Keep responses concise and actionable
- If a user mentions a minor injury, suggest remedies but recommend seeing a doctor
- Never encourage unsafe or extreme practices
- Tailor advice to the user's experience level
```

**Keyword score: 100% (38/38)** after fixing two assertion bugs surfaced during eval.  
**LLM judge: not applied**

---

### v2 — Structured with category-specific guidelines
Added explicit behavior rules per scenario category.
```
You are an experienced personal fitness trainer. Give practical, concise advice 
tailored to the user.

Guidelines:
- Be direct and to the point — no filler or unnecessary encouragement
- For beginners: keep it simple, max 4 steps, use plain language, avoid jargon
- For advanced users: use proper training terminology, give specific programming advice
- For equipment questions: give clear step-by-step instructions
- For muscle-specific questions: name the exact exercises and why they work
- For vague inputs: ask one clarifying question, then give a starting point
- For injuries: suggest 2-3 specific remedies, then recommend seeing a doctor
- Never recommend unsafe practices like extreme calorie restriction or training 
  every day without rest
```

**Keyword score: 97% (37/38)**  
**LLM judge: 13/13** after fixing one prompt issue surfaced by the judge.

---

## Failures & What I Learned

### Failure 1 — Advanced question flagged as too long
**Test case:** "I'm training for a powerlifting meet in 8 weeks, how should I peak?"  
**Assertion failed:** `concise` (150 word limit)  
**Keyword score:** 2/3 — **LLM judge:** not applied  

**Root cause:** The 150 word concise limit was too strict for complex advanced 
questions that legitimately require detailed answers.  

**Fix:** Added a `concise_extended` assertion (250 word limit) and applied it 
to advanced category test cases instead of `concise`.  

**Lesson:** Assertions should be context-aware. A single rule applied uniformly 
across all categories will produce false negatives for valid responses.

---

### Failure 2 — Clarifying question flagged as not addressing input
**Test case:** "Just make me fit"  
**Assertion failed:** `addresses_input` (response under 30 words)  
**Keyword score:** 2/3 — **LLM judge:** not applied  

**Root cause:** The v2 prompt correctly instructs the model to ask a clarifying 
question for vague inputs. The assertion penalized correct behavior because it 
only checked word count.  

**Fix:** Updated `addresses_input` to pass if the response contains a clarifying 
question, even if short.  

**Lesson:** When an assertion fails, the bug is sometimes in the assertion itself, 
not the prompt. Diagnosing which one is wrong is a core eval skill.

---

### Failure 3 — Beginner equipment response too complex
**Test case:** "How do I use the assisted pull-up machine?"  
**Keyword score:** 3/3 ✅ — **LLM judge:** failed ❌  

**Root cause:** The response had 6 detailed steps with technical language. 
Keyword assertions passed because the response was actionable and concise by 
word count — but the LLM judge correctly identified it as overwhelming for a beginner.  

**Fix:** Updated the prompt to cap beginner responses at 4 steps and require 
plain language with explanations for any technical terms used.  

**Lesson:** Keyword assertions cannot detect response quality or complexity. 
LLM-as-judge catches qualitative failures that rules cannot express. This is 
the core reason to use both layers together.

---

## Results Summary

| Prompt | Keyword Score | LLM Judge | Notes |
|--------|--------------|-----------|-------|
| v1 | 97% → 100% | — | Fixed 2 assertion bugs during eval |
| v2 | 95% → 100% | 12/13 → 13/13 | Fixed 1 assertion bug + 1 prompt issue |

---

## Limitations
- **Keyword assertions are brittle** — checking for "doctor" doesn't guarantee 
  the advice is medically sound, just that the word appears
- **LLM judge is non-deterministic** — running the same response twice can 
  produce different verdicts, making scores noisy across runs
- **Small test set** — 13 cases is enough to learn the concepts but not enough 
  to be statistically meaningful in production
- **No human evaluation** — a real eval suite would include human review for a 
  sample of responses, especially for safety-critical categories like injury

---

## Next Steps
- Expand test set to 50+ cases using real user queries
- Add a third prompt version with few-shot examples and measure impact
- Run each test case 3x and average LLM judge scores to reduce noise
- Add human review pass for injury and unsafe categories