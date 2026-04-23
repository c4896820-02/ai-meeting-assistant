import json
from pathlib import Path
from main import run_pipeline


BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_PATH = BASE_DIR / "data" / "eval_cases.json"


def load_eval_cases():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate():
    cases = load_eval_cases()

    total = len(cases)
    topic_hit = 0
    action_count_hit = 0

    results = []

    for case in cases:
        output = run_pipeline(case["input"])

        predicted_topic = output.get("meeting_topic", "")
        predicted_action_count = len(output.get("action_items", []))

        topic_ok = case["expected_topic"] in predicted_topic or predicted_topic in case["expected_topic"]
        action_ok = predicted_action_count == case["expected_action_count"]

        if topic_ok:
            topic_hit += 1
        if action_ok:
            action_count_hit += 1

        results.append({
            "id": case["id"],
            "predicted_topic": predicted_topic,
            "predicted_action_count": predicted_action_count,
            "topic_match": topic_ok,
            "action_count_match": action_ok
        })

    print("===== 评测结果 =====")
    print(f"总样本数: {total}")
    print(f"主题命中数: {topic_hit}/{total}")
    print(f"待办数量命中数: {action_count_hit}/{total}")

    print("\n===== 逐条结果 =====")
    for item in results:
        print(item)


if __name__ == "__main__":
    evaluate()