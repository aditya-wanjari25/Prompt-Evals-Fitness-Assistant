# Prompt Evals - Fitness Assistant

A prompt evaluation suite for an AI personal fitness trainer, built to systematically test and improve LLM prompt quality.

## What this does
- Runs 13 test cases across 6 categories (beginner, muscle-specific, injury, vague, advanced, unsafe)
- Scores each response against targeted assertions (concise, actionable, safe, refers_doctor)
- Saves timestamped results to track improvement across prompt versions

## Setup
```bash
pip install -r requirements.txt
```
Add your OpenAI key to a `.env` file:
```
OPENAI_API_KEY=your-key-here
```

## Run
```bash
python run_evals.py
```

## Results
| Prompt Version | Score | Date |
|---|---|---|
| v1 | 100% (38/38) | Mar, 7 2026|
| v2 | 97% (37/38) | Mar, 7 2026|