"""Text extraction from PDF, images, and plain text files."""

import os
import base64
from pathlib import Path
from io import BytesIO
from typing import List, Tuple


def extract_pdf(filepath: str) -> List[Tuple[int, str]]:
    """Extract text from PDF, returning list of (page_num, text)."""
    import fitz
    doc = fitz.open(filepath)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append((i + 1, text.strip()))
    doc.close()
    return pages


def extract_image(filepath: str) -> bytes:
    """Load image as bytes for vision API."""
    from PIL import Image
    img = Image.open(filepath)
    if img.mode == "RGBA":
        img = img.convert("RGB")
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def extract_text_file(filepath: str) -> str:
    """Read plain text or markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_source(filepath: str) -> dict:
    """Auto-detect file type and extract content."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        pages = extract_pdf(filepath)
        full_text = "\n\n".join(f"[第{p}页]\n{t}" for p, t in pages)
        return {"type": "pdf", "content": full_text, "pages": len(pages)}
    elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        img_bytes = extract_image(filepath)
        return {"type": "image", "content": img_bytes}
    elif ext in (".txt", ".md", ".markdown"):
        text = extract_text_file(filepath)
        return {"type": "text", "content": text}
    else:
        raise ValueError(f"不支持的文件类型: {ext}，支持的格式: .pdf, .png, .jpg, .jpeg, .bmp, .webp, .txt, .md")
