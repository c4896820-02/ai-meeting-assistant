import os
import json
from pathlib import Path
from openai import OpenAI


# ===== 路径配置 =====
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "sample_meeting.txt"
PROMPT_PATH = BASE_DIR / "prompt" / "meeting_prompt.txt"
OUTPUT_PATH = BASE_DIR / "output" / "result.json"


# ===== 读取文件 =====
def read_text_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ===== 构建 Prompt =====
def build_prompt(template: str, content: str) -> str:
    return template.replace("{content}", content)


# ===== 提取 JSON 文本 =====
def extract_json_text(text: str) -> str:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        return text[start:end + 1].strip()

    return text


# ===== 创建客户端 =====
def get_client() -> OpenAI:
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        raise ValueError("未读取到环境变量 MOONSHOT_API_KEY，请先配置 API Key")

    return OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1"
    )


# ===== 修复 JSON =====
def repair_json(raw_text: str) -> dict:
    client = get_client()

    repair_prompt = f"""
你是一个 JSON 修复助手。
下面是一段本应为 JSON 的文本，但格式可能不合法。

你的任务：
1. 修复它，使其成为合法 JSON
2. 不允许添加解释
3. 不允许输出 Markdown 代码块
4. 只输出修复后的 JSON 对象

待修复内容：
{raw_text}
"""

    response = client.chat.completions.create(
        model="kimi-k2.5",
        messages=[
            {"role": "system", "content": "你是一个严格输出合法JSON的助手"},
            {"role": "user", "content": repair_prompt}
        ]
    )

    repaired_content = response.choices[0].message.content
    print("\n===== 修复后的模型输出 =====")
    print(repaired_content)

    cleaned = extract_json_text(repaired_content)
    return json.loads(cleaned)


# ===== 调用大模型 =====
def call_llm(prompt: str) -> dict:
    client = get_client()

    response = client.chat.completions.create(
        model="kimi-k2.5",
        messages=[
            {
                "role": "system",
                "content": "你是一个严格输出JSON的助手。你必须只输出合法JSON对象，不允许输出任何额外解释。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    print("\n===== 模型原始输出 =====")
    print(content)

    cleaned = extract_json_text(content)

    print("\n===== 清洗后 JSON 文本 =====")
    print(cleaned)

    try:
        return json.loads(cleaned)
    except Exception as e:
        print("\n❌ 首次 JSON 解析失败：", e)
        print("开始尝试自动修复 JSON ...")

        try:
            return repair_json(content)
        except Exception as repair_error:
            print("\n❌ JSON 修复仍然失败：", repair_error)
            return {
                "error": "JSON解析失败且修复失败",
                "raw_output": content,
                "cleaned_output": cleaned
            }


# ===== 保存结果 =====
def save_result(result: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


# ===== 主流程 =====
def main() -> None:
    meeting_content = read_text_file(DATA_PATH)
    prompt_template = read_text_file(PROMPT_PATH)

    final_prompt = build_prompt(prompt_template, meeting_content)

    result = call_llm(final_prompt)
    save_result(result, OUTPUT_PATH)

    print("\n✅ 结果已保存到：", OUTPUT_PATH)


if __name__ == "__main__":
    main()