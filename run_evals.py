import json
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from assertions.checks import ASSERTION_MAP
from assertions.llm_judge import llm_judge  

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_prompt(version="v1"):
    with open(f"prompts/{version}.txt", "r") as f:
        return f.read()

def load_test_cases():
    with open("test_cases/cases.json", "r") as f:
        return json.load(f)

def get_response(message, prompt):
    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]
    )
    return result.choices[0].message.content

def score_response(response, assertions):
    results = {}
    for name in assertions:
        fn = ASSERTION_MAP[name]
        results[name] = fn(response)
    passed = sum(results.values())
    total = len(results)
    return {"results": results, "score": passed, "total": total}

def run_evals(version="v1"):
    prompt = load_prompt(version)
    test_cases = load_test_cases()

    run_results = []
    total_passed = 0
    total_assertions = 0

    print(f"\n🏋️  Running evals — prompt {version}\n{'='*50}")

    for tc in test_cases:
        response = get_response(tc["message"], prompt)
        scored = score_response(response, tc["assertions"])
        judge = llm_judge(client, response, tc["category"])  

        total_passed += scored["score"]
        total_assertions += scored["total"]

        print(f"\n[{tc['category'].upper()}] {tc['message']}")
        print(f"Response: {response[:120]}...")
        for assertion, passed in scored["results"].items():
            print(f"  {'✅' if passed else '❌'} {assertion}")
        print(f"  Score: {scored['score']}/{scored['total']}")
        judge_icon = "✅" if judge["passed"] else "❌"
        print(f"  {judge_icon} LLM judge: {judge['reason']}")  

        run_results.append({
            "id": tc["id"],
            "category": tc["category"],
            "message": tc["message"],
            "response": response,
            "scored": scored,
            "llm_judge": judge  
        })

    overall = round((total_passed / total_assertions) * 100)
    llm_passes = sum(1 for r in run_results if r["llm_judge"]["passed"])  
    llm_total = len(run_results)  

    print(f"\n{'='*50}")
    print(f"✅ Keyword score: {total_passed}/{total_assertions} ({overall}%)")
    print(f"🤖 LLM judge: {llm_passes}/{llm_total} passed")  

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = {
        "prompt_version": version,
        "timestamp": timestamp,
        "overall_score": overall,
        "llm_judge_score": f"{llm_passes}/{llm_total}",  
        "results": run_results
    }
    os.makedirs("results", exist_ok=True)
    with open(f"results/{version}_{timestamp}.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"💾 Results saved to results/{version}_{timestamp}.json\n")
    return overall

if __name__ == "__main__":
    v1_score = run_evals("v1")
    v2_score = run_evals("v2")

    print(f"📊 Comparison")
    print(f"  v1: {v1_score}%")
    print(f"  v2: {v2_score}%")
    if v2_score >= v1_score:
        print(f"  ✅ v2 holds or improves on v1")
    else:
        print(f"  ⚠️  v2 regressed — check the failures")