"""Generate organized markdown notes from analyzed knowledge structure."""

import os
from datetime import date
from .config import Config


def generate_notes(analysis: dict, config: Config) -> str:
    """Generate organized hierarchical markdown notes."""
    output_dir = config.output_dir
    os.makedirs(output_dir, exist_ok=True)
    subject = analysis.get("subject", config.subject)

    chapters_text = _render_toc(analysis.get("chapters", []))

    chapters_detail = ""
    for ch in analysis.get("chapters", []):
        chapters_detail += _render_chapter(ch)

    index_md = f"""# {subject} 学习笔记

> 自动生成于 {date.today().isoformat()}

---

## 目录

{chapters_text}

---

{chapters_detail}
"""
    index_path = os.path.join(output_dir, "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_md)

    for ch in analysis.get("chapters", []):
        ch_dir = os.path.join(output_dir, _slugify(ch.get("title", "unknown")))
        os.makedirs(ch_dir, exist_ok=True)
        _save_chapter_files(ch, ch_dir)

    return index_md


def _render_toc(chapters: list) -> str:
    lines = []
    for ch in chapters:
        lines.append(f"- [{ch['title']}]({_slugify(ch['title'])}/README.md)")
        for sec in ch.get("sections", []):
            lines.append(f"  - [{sec['title']}]({_slugify(ch['title'])}/{_slugify(sec['title'])}.md)")
    return "\n".join(lines)


def _render_chapter(ch: dict) -> str:
    lines = [f"## 第{ch['order']}章 {ch['title']}\n"]
    for sec in ch.get("sections", []):
        lines.append(f"### {sec['title']}\n")
        for c in sec.get("concepts", []):
            lines.append(f"#### {c['name']}\n")
            lines.append(f"{c['explanation']}\n")

            if c.get("formulas"):
                lines.append("**核心公式：**\n")
                for f in c["formulas"]:
                    lines.append(f"\n{f}\n")
                lines.append("")

            if c.get("key_points"):
                lines.append("**要点：**\n")
                for kp in c["key_points"]:
                    lines.append(f"- {kp}")
                lines.append("")

            if c.get("common_mistakes"):
                lines.append("**常见错误：**\n")
                for cm in c["common_mistakes"]:
                    lines.append(f"- ⚠️ {cm}")
                lines.append("")

            related = c.get("related_concepts", [])
            if related:
                lines.append("**关联概念：** " + " · ".join(
                    f"[[{r}]]" for r in related
                ) + "\n")

            lines.append(f"*难度：{'⭐' * c.get('difficulty', 3)}*\n")
            lines.append("---\n")
    return "\n".join(lines)


def _render_concept_detail(c: dict) -> str:
    lines = [f"# {c['name']}\n"]
    lines.append(f"**难度**：{'⭐' * c.get('difficulty', 3)}  \n")
    lines.append(f"**所属章节**：{c.get('section', '')}  \n")
    lines.append(f"\n## 概念解释\n\n{c['explanation']}\n")

    if c.get("formulas"):
        lines.append("## 核心公式\n")
        for f in c["formulas"]:
            lines.append(f"\n{f}\n")
        lines.append("")

    if c.get("key_points"):
        lines.append("## 关键要点\n")
        for kp in c["key_points"]:
            lines.append(f"- {kp}")
        lines.append("")

    if c.get("common_mistakes"):
        lines.append("## ⚠️ 常见错误\n")
        for cm in c["common_mistakes"]:
            lines.append(f"- {cm}")
        lines.append("")

    if c.get("related_concepts"):
        lines.append("## 相关概念\n")
        for r in c["related_concepts"]:
            lines.append(f"- [[{r}]]")
        lines.append("")

    return "\n".join(lines)


def _save_chapter_files(ch: dict, ch_dir: str):
    ch_readme = [f"# 第{ch['order']}章 {ch['title']}\n"]
    for sec in ch.get("sections", []):
        slug = _slugify(sec["title"])
        ch_readme.append(f"- [{sec['title']}]({slug}.md)")

        sec_lines = [f"# {sec['title']}\n"]
        for c in sec.get("concepts", []):
            c["section"] = sec["title"]
            sec_lines.append(_render_concept_detail(c))
            sec_lines.append("\n---\n")

        sec_path = os.path.join(ch_dir, f"{slug}.md")
        with open(sec_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sec_lines))

    readme_path = os.path.join(ch_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ch_readme))


def _slugify(text: str) -> str:
    import re
    # 保留中文字符、英文字母、数字
    text = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    result = text.strip('-')
    # 如果结果为空（纯特殊字符），用hash生成目录名
    if not result:
        import hashlib
        result = hashlib.md5(text.encode()).hexdigest()[:8]
    return result
