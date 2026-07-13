"""自动高数笔记本 - AI驱动的数学学习助手"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import date

from math_notebook.config import Config, get_default_config
from math_notebook.extractor import extract_source
from math_notebook.analyzer import analyze_content, generate_daily_review, deep_explain
from math_notebook.organizer import generate_notes
from math_notebook.graph_gen import generate_graph
from math_notebook.review import save_daily_review, generate_review_history
from math_notebook.exporter import export_for_notebooklm

console = Console()


@click.group()
@click.pass_context
def cli(ctx):
    """📚 自动高数笔记本 - 从教材到知识体系的AI助手"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = get_default_config()


@cli.command()
@click.argument("filepath")
@click.option("-o", "--output", default=None, help="输出目录")
@click.option("--subject", default="高等数学", help="学科名称")
@click.pass_context
def scan(ctx, filepath, output, subject):
    """扫描教材/讲义，自动提取知识点并生成结构化笔记"""
    config = ctx.obj["config"]
    if output:
        config.output_dir = output
    config.subject = subject

    if not config.api_key:
        console.print("[red]❌ 请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量[/red]")
        console.print("[dim]macOS 设置方法: export DEEPSEEK_API_KEY=\"sk-xxxx\"[/dim]")
        return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("[cyan]正在提取文本...", total=None)
        source = extract_source(filepath)
        progress.update(task, description=f"[green]✓ 提取完成 ({source['type']}, {len(str(source['content']))} 字符)")

        task = progress.add_task("[cyan]AI 正在分析知识点...", total=None)
        analysis = analyze_content(source, config)
        progress.update(task, description="[green]✓ 知识点提取完成")

        chapters = analysis.get("chapters", [])
        total_concepts = sum(len(sec.get("concepts", [])) for ch in chapters for sec in ch.get("sections", []))
        console.print(f"\n[bold]📊 分析结果：[/bold]{len(chapters)} 章, {total_concepts} 个知识点")

        task = progress.add_task("[cyan]生成笔记文件...", total=None)
        generate_notes(analysis, config)
        progress.update(task, description="[green]✓ 笔记生成完成")

        task = progress.add_task("[cyan]生成知识图谱...", total=None)
        generate_graph(analysis, config.output_dir)
        progress.update(task, description="[green]✓ 知识图谱生成完成")

    console.print(f"\n[bold green]✅ 完成！[/bold green] 笔记目录: {config.output_dir}")
    _print_summary(analysis)


@cli.command()
@click.option("-o", "--output", default=None, help="输出目录")
@click.option("--topic", default=None, help="指定主题/章节")
@click.pass_context
def review(ctx, output, topic):
    """生成今日复习计划"""
    config = ctx.obj["config"]
    if output:
        config.output_dir = output

    if not config.api_key:
        console.print("[red]❌ 请设置 API Key[/red]")
        return

    notes_dir = config.output_dir
    index_path = os.path.join(notes_dir, "index.md")

    if not os.path.exists(index_path):
        console.print("[yellow]⚠️ 还没有笔记，请先运行 scan 扫描教材[/yellow]")
        return

    all_concepts = _load_concepts_from_notes(notes_dir)
    if topic:
        all_concepts = [c for c in all_concepts if topic in c.get("name", "") or topic in c.get("section", "")]

    if not all_concepts:
        console.print("[yellow]⚠️ 未找到知识点，请先运行 scan[/yellow]")
        return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("[cyan]AI 正在生成复习计划...", total=None)
        review_data = generate_daily_review(all_concepts[:20], config)
        progress.update(task, description="[green]✓ 复习计划生成完成")

        task = progress.add_task("[cyan]保存复习笔记...", total=None)
        filepath = save_daily_review(review_data, notes_dir)
        progress.update(task, description="[green]✓ 保存完成")

    generate_review_history(notes_dir)
    _print_review(review_data)
    console.print(f"\n[green]📄 已保存到: {filepath}[/green]")


@cli.command()
@click.argument("concept")
@click.option("--topic", default="高等数学", help="主题")
@click.pass_context
def explain(ctx, concept, topic):
    """详细讲解某个知识点"""
    config = ctx.obj["config"]

    if not config.api_key:
        console.print("[red]❌ 请设置 API Key[/red]")
        return

    notes_dir = config.output_dir
    context = ""
    index_path = os.path.join(notes_dir, "index.md")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            context = f.read()[:3000]

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("[cyan]AI 正在准备讲解...", total=None)
        explanation = deep_explain(topic, concept, context, config)
        progress.update(task, description="[green]✓")

    console.print(Panel(Markdown(explanation), title=f"📖 {concept}", border_style="blue"))


@cli.command()
@click.option("-o", "--output", default=None, help="输出目录")
@click.pass_context
def export(ctx, output):
    """导出为PDF（用于上传NotebookLM）"""
    config = ctx.obj["config"]
    if output:
        config.output_dir = output

    pdf_path = export_for_notebooklm(config.output_dir)
    if pdf_path:
        console.print(f"[green]✅ PDF 已导出: {pdf_path}[/green]")
    else:
        console.print("[red]❌ 导出失败，请确保已运行 scan 且安装了 weasyprint[/red]")


@cli.command()
@click.option("-o", "--output", default=None, help="输出目录")
@click.pass_context
def status(ctx, output):
    """查看当前知识体系状态"""
    config = ctx.obj["config"]
    if output:
        config.output_dir = output

    notes_dir = config.output_dir
    if not os.path.exists(notes_dir):
        console.print("[yellow]还没有笔记[/yellow]")
        return

    concepts = _load_concepts_from_notes(notes_dir)
    review_dir = os.path.join(notes_dir, "每日复习")
    review_count = 0
    if os.path.exists(review_dir):
        review_count = len([f for f in os.listdir(review_dir) if f.endswith(".md") and f != "README.md"])

    table = Table(title="📊 知识体系状态")
    table.add_column("指标", style="cyan")
    table.add_column("数值", style="green")
    table.add_row("知识点总数", str(len(concepts)))
    table.add_row("复习次数", str(review_count))
    table.add_row("笔记目录", notes_dir)
    console.print(table)


@cli.command()
def setup():
    """交互式配置"""
    console.print("[bold]🔧 配置向导[/bold]\n")

    api_key = click.prompt("API Key (DeepSeek 或 OpenAI)", default="", show_default=False)
    model = click.prompt("模型名称", default="deepseek-chat")
    api_base = click.prompt("API地址", default="https://api.deepseek.com/v1")

    config = Config(api_key=api_key, api_base=api_base, model=model)
    config.save()

    console.print("\n[green]✅ 配置已保存到 config.json[/green]")
    console.print("[dim]获取 DeepSeek API Key: https://platform.deepseek.com[/dim]")


def _print_summary(analysis: dict):
    chapters = analysis.get("chapters", [])
    table = Table(title="📋 知识结构")
    table.add_column("章节", style="cyan")
    table.add_column("知识点", style="green")
    table.add_column("难度", style="yellow")

    for ch in chapters:
        for sec in ch.get("sections", []):
            for c in sec.get("concepts", []):
                stars = "⭐" * c.get("difficulty", 3)
                table.add_row(f"{ch['title']} > {sec['title']}", c["name"], stars)

    console.print(table)


def _print_review(review_data: dict):
    console.print(f"\n[bold]📝 {review_data.get('date', '')} 复习计划[/bold]\n")

    for i, q in enumerate(review_data.get("review_questions", []), 1):
        console.print(f"[cyan]第{i}题[/cyan] {q['question']}")

    console.print(f"\n[bold yellow]📐 重点公式:[/bold yellow]")
    for f in review_data.get("key_formulas", []):
        console.print(f"  • {f}")

    cc = review_data.get("concept_clarification", {})
    if cc:
        console.print(f"\n[bold magenta]🔀 {cc.get('concept_a', '')} vs {cc.get('concept_b', '')}[/bold magenta]")
        console.print(f"  {cc.get('difference', '')}")


def _load_concepts_from_notes(notes_dir: str) -> list:
    concepts = []
    if not os.path.exists(notes_dir):
        return concepts

    for root, dirs, files in os.walk(notes_dir):
        for f in files:
            if f.endswith(".md") and f not in ("index.md", "README.md", "knowledge_graph.md"):
                filepath = os.path.join(root, f)
                with open(filepath, "r", encoding="utf-8") as fp:
                    content = fp.read()
                for line in content.split("\n"):
                    if line.startswith("# "):
                        name = line[2:].strip()
                        if name and not name.startswith("📝") and not name.startswith("第") and not name.startswith("📖"):
                            section = os.path.basename(root)
                            concepts.append({"name": name, "section": section, "explanation": content[:200]})
                        break
    return concepts


if __name__ == "__main__":
    cli()
