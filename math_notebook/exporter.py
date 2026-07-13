"""Export notes to PDF for NotebookLM upload."""

import os
import markdown


def export_to_pdf(markdown_content: str, output_path: str):
    """Convert markdown to a clean PDF suitable for NotebookLM."""
    try:
        from weasyprint import HTML

        html_body = markdown.markdown(
            markdown_content,
            extensions=["extra", "codehilite", "tables", "toc"]
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: "PingFang SC", "Microsoft YaHei", sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.8; color: #333; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #16213e; padding-bottom: 10px; }}
h2 {{ color: #0f3460; border-bottom: 2px solid #e94560; padding-bottom: 8px; }}
h3 {{ color: #16213e; }}
h4 {{ color: #533483; }}
blockquote {{ background: #f0f0f0; border-left: 4px solid #e94560; padding: 10px 20px; margin: 16px 0; }}
details {{ background: #fafafa; border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 10px 0; }}
details summary {{ cursor: pointer; font-weight: bold; color: #e94560; }}
code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
pre {{ background: #1a1a2e; color: #eee; padding: 16px; border-radius: 8px; overflow-x: auto; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

        HTML(string=html).write_pdf(output_path)
        return output_path
    except ImportError:
        return None


def export_for_notebooklm(output_dir: str) -> str:
    """Gather all notes into a single PDF for NotebookLM upload."""
    index_path = os.path.join(output_dir, "index.md")
    if not os.path.exists(index_path):
        return None

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    pdf_path = os.path.join(output_dir, "notebooklm_export.pdf")
    result = export_to_pdf(content, pdf_path)
    return result
