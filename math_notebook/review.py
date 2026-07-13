"""Generate daily review notes and save to structured markdown."""

import os
import json
from datetime import date, timedelta


def save_daily_review(review_data: dict, output_dir: str) -> str:
    """Save daily review as a structured markdown file."""
    review_dir = os.path.join(output_dir, "每日复习")
    os.makedirs(review_dir, exist_ok=True)

    d = review_data.get("date", date.today().isoformat())
    filename = f"{d}.md"
    filepath = os.path.join(review_dir, filename)

    md = [f"# 📝 每日复习 - {d}\n"]

    md.append("## 🔥 今日回顾题\n")
    for i, q in enumerate(review_data.get("review_questions", []), 1):
        md.append(f"### 第{i}题\n")
        md.append(f"**题目：** {q['question']}\n")
        md.append(f"**关联知识点：** {q.get('related_concept', '')}\n")
        md.append(f"<details>\n<summary>查看解答</summary>\n\n{q['solution']}\n</details>\n")

    md.append("## 📐 重点公式\n")
    for f in review_data.get("key_formulas", []):
        md.append(f"- {f}")
    md.append("")

    cc = review_data.get("concept_clarification", {})
    if cc:
        md.append("## 🔀 概念辨析\n")
        md.append(f"**{cc.get('concept_a', '')}** vs **{cc.get('concept_b', '')}**\n")
        md.append(f"{cc.get('difference', '')}\n")

    ps = review_data.get("preview_suggestion", "")
    if ps:
        md.append(f"## 📖 明日预习\n\n{ps}\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    return filepath


def generate_review_history(output_dir: str):
    """Generate review history index listing all daily reviews."""
    review_dir = os.path.join(output_dir, "每日复习")
    os.makedirs(review_dir, exist_ok=True)

    index_path = os.path.join(review_dir, "README.md")
    files = sorted(
        [f for f in os.listdir(review_dir) if f.endswith(".md") and f != "README.md"],
        reverse=True
    )

    lines = ["# 复习记录\n"]
    for f in files:
        name = f.replace(".md", "")
        lines.append(f"- [{name}]({f})")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
