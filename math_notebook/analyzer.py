"""LLM-powered knowledge analysis: concept extraction, organization, and explanation."""

import json
import base64
import re
from datetime import date
from openai import OpenAI
from .config import Config


SYSTEM_PROMPT = """你是一个高等数学教学专家。你的任务是从学习材料中提取、整理知识点。

对于每个知识点，你需要提供：
1. 知识点名称
2. 所属章节/主题
3. 核心概念解释（通俗易懂）
4. 关键公式（LaTeX格式）
5. 典型例题
6. 易错点
7. 与其他知识点的关联
8. 重要性分类（必背/理解/了解）
9. 记忆方式（背诵/做题理解）

输出格式：严格按照JSON格式，不要输出其他内容。"""


EXTRACT_PROMPT = """请从以下内容中提取所有知识点，按章节层级组织。

{content}

请输出JSON（不要用markdown代码块包裹，只输出纯JSON）：
{
  "subject": "学科名称",
  "chapters": [
    {
      "title": "章标题",
      "order": 1,
      "sections": [
        {
          "title": "节标题",
          "order": 1,
          "concepts": [
            {
              "name": "知识点名称",
              "explanation": "通俗解释",
              "formulas": ["$$公式1$$", "$$公式2$$"],
              "key_points": ["要点1", "要点2"],
              "common_mistakes": ["易错点1"],
              "related_concepts": ["关联知识点名称"],
              "difficulty": 1-5,
              "importance": "必背/理解/了解",
              "memory_type": "背诵/做题理解",
              "is_exam_key": true/false
            }
          ]
        }
      ]
    }
  ]
}

重要性分类说明：
- 必背：核心公式、基本定理、必须牢记的内容
- 理解：需要通过做题和思考才能掌握的概念
- 了解：辅助性知识、拓展内容

记忆方式说明：
- 背诵：需要反复记忆的内容（公式、定理、定义）
- 做题理解：需要通过练习才能掌握的内容（解题方法、证明思路）"""


DAILY_REVIEW_PROMPT = """你是一位高数辅导老师。根据以下已学知识点，生成今日复习内容。

已学知识点：
{concepts_summary}

请生成今日复习计划，包含：
1. 5道回顾题（附带详细解答步骤）
2. 3个需要重点记忆的公式
3. 1个易混淆概念辨析
4. 明日预习建议

输出JSON：
{
  "date": "YYYY-MM-DD",
  "review_questions": [
    {"question": "题目", "solution": "详细解答步骤", "related_concept": "关联知识点"}
  ],
  "key_formulas": ["公式及说明"],
  "concept_clarification": {"concept_a": "概念A", "concept_b": "概念B", "difference": "区别"},
  "preview_suggestion": "预习建议"
}"""


def _parse_json_response(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks and extra text."""
    text = text.strip()
    # 去除markdown代码块包裹
    code_block = re.match(r'^```(?:json)?\s*\n(.*?)\n```$', text, re.DOTALL)
    if code_block:
        text = code_block.group(1).strip()
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试提取第一个完整的JSON对象
    brace_count = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if start is None:
                start = i
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0 and start is not None:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    start = None
    raise ValueError(f"无法从LLM响应中解析JSON: {text[:200]}...")


def get_client(config: Config) -> OpenAI:
    return OpenAI(api_key=config.api_key, base_url=config.api_base)


def analyze_content(source_data: dict, config: Config) -> dict:
    """Extract knowledge points from source content."""
    client = get_client(config)
    content = source_data.get("content", "")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    if source_data["type"] == "image":
        img_b64 = base64.b64encode(content).decode()
        messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                {"type": "text", "text": EXTRACT_PROMPT.format(content="[图片内容]")},
            ]
        })
    else:
        max_len = 30000
        truncated = content[:max_len] if len(content) > max_len else content
        messages.append({"role": "user", "content": EXTRACT_PROMPT.format(content=truncated)})

    response = client.chat.completions.create(
        model=config.model,
        messages=messages,
        temperature=0.3,
    )

    result_text = response.choices[0].message.content.strip()
    return _parse_json_response(result_text)


def generate_daily_review(concepts: list, config: Config) -> dict:
    """Generate daily review plan from learned concepts."""
    client = get_client(config)

    summary_lines = []
    for c in concepts:
        name = c.get("name", "")
        explanation = c.get("explanation", "")[:100]
        summary_lines.append(f"- {name}: {explanation}")
    concepts_summary = "\n".join(summary_lines)

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": "你是高数辅导老师，用中文输出。输出纯JSON。"},
            {"role": "user", "content": DAILY_REVIEW_PROMPT.format(concepts_summary=concepts_summary)},
        ],
        temperature=0.5,
    )

    result_text = response.choices[0].message.content.strip()
    data = _parse_json_response(result_text)
    if "date" not in data:
        data["date"] = date.today().isoformat()
    return data


def deep_explain(topic: str, concept_name: str, context: str, config: Config) -> str:
    """Get a detailed AI explanation for a specific concept."""
    client = get_client(config)

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": f"你正在讲解高等数学中的{topic}。用通俗易懂的中文讲解，配合具体例子。如果涉及公式，用LaTeX格式 $$...$$。"},
            {"role": "user", "content": f"请详细讲解：{concept_name}\n\n上下文：{context}"},
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content
