import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from src.analyzer import analyze_prompt
from src.improver import run_improvement_cycle
from src.exporter import export_artifacts
from src.stress_tester import run_stress_test
from src.optimizer import optimize_prompt

console = Console()

def display_welcome():
    console.print(Panel.fit(
        "[bold cyan]Prompt Inspector v0.2.0[/bold cyan]\n"
        "[dim]Full Lifecycle Validation & Hardening[/dim]",
        border_style="cyan"
    ))

def get_user_input():
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    
    console.print("\n[bold]Paste your prompt[/bold] (Ctrl+D/Ctrl+Z when finished):")
    return sys.stdin.read().strip()

def run():
    display_welcome()
    prompt = get_user_input()
    
    if not prompt:
        console.print("[red]No prompt provided. Exiting.[/red]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        # Step 1: Initial Analysis
        progress.add_task(description="Analyzing original prompt...", total=None)
        analysis = analyze_prompt(prompt)
        if not analysis:
            console.print("[red]Analysis failed.[/red]")
            return

        # Step 2: Prompt Optimizer
        progress.add_task(description="Optimizing prompt structure and intent...", total=None)
        optimizer = optimize_prompt(prompt)

        # Step 3: Improvement Cycle
        progress.add_task(description="Iteratively improving & re-scoring...", total=None)
        comparison = run_improvement_cycle(prompt, analysis)

        # Step 4: Stress Testing
        progress.add_task(description="Running adversarial stress tests...", total=None)
        stress_results = run_stress_test(analysis.improved_prompt, analysis.adversarial_variants)

        # Step 5: Export
        progress.add_task(description="Generating artifacts...", total=None)
        export_path = export_artifacts(prompt, analysis, comparison, stress_results)

    # --- UI Output ---
    
    # 1. Classification & Overview
    console.print(Panel(
        f"[bold blue]Types:[/bold blue] {', '.join(analysis.prompt_types)}\n"
        f"[bold blue]Task:[/bold blue] {analysis.parsing.task or 'N/A'}\n"
        f"[bold blue]Role:[/bold blue] {analysis.parsing.role or 'N/A'}",
        title="[bold white]Prompt Overview[/bold white]",
        border_style="blue"
    ))

    # 2. Quality Table
    table = Table(title="Quality Comparison (Original vs Improved)", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="dim")
    table.add_column("Original", justify="center")
    table.add_column("Improved", justify="center")
    table.add_column("Delta", justify="right")

    for k, v in comparison.delta.items():
        if k == 'readability_score': continue
        color = "green" if v > 0 else "red" if v < 0 else "white"
        table.add_row(
            k.capitalize(),
            str(comparison.original_scores.model_dump()[k]),
            str(comparison.improved_scores.model_dump()[k]),
            f"[{color}]{v:+} [/{color}]"
        )
    
    # Add Readability Row
    r_orig = comparison.original_scores.readability_score or 0
    r_imp = comparison.improved_scores.readability_score or 0
    r_delta = r_imp - r_orig
    r_color = "cyan" if r_delta >= 0 else "yellow"
    table.add_row(
        "Readability (Flesch)",
        f"{r_orig:.1f}",
        f"{r_imp:.1f}",
        f"[{r_color}]{r_delta:+.1f}[/{r_color}]"
    )

    console.print(table)

    # 3. Stress Test Results
    if stress_results:
        stress_table = Table(title="Adversarial Robustness Report", show_header=True, header_style="bold red")
        stress_table.add_column("Attack Vector")
        stress_table.add_column("Status", justify="center")
        stress_table.add_column("Risk", justify="center")
        stress_table.add_column("Observation", style="dim", width=60)

        for res in stress_results:
            status = "[bold green]SECURE[/bold green]" if res.passed else "[bold red]VULNERABLE[/bold red]"
            risk_color = "red" if res.risk_level.lower() == "high" else "yellow" if res.risk_level.lower() == "medium" else "green"
            stress_table.add_row(
                res.variant_type,
                status,
                f"[{risk_color}]{res.risk_level}[/{risk_color}]",
                res.observation
            )
        console.print(stress_table)

    # 4. Vulnerabilities
    if analysis.vulnerabilities:
        console.print(Panel(
            "\n".join([f"[red]•[/red] {v}" for v in analysis.vulnerabilities]),
            title="[bold red]Detected Vulnerabilities[/bold red]",
            border_style="red"
        ))

    # 5. Optimizer Summary
    if optimizer:
        console.print(Panel(
            f"[bold cyan]Summary:[/bold cyan] {optimizer.summary}\n\n"
            f"[bold yellow]Why it is better:[/bold yellow] {optimizer.why_better}\n\n"
            + "\n".join(f"• {step.name}: {step.explanation}" for step in optimizer.steps),
            title="[bold magenta]Prompt Optimizer[/bold magenta]",
            border_style="magenta"
        ))

    # 6. Improved Prompt Preview
    console.print(Panel(
        Markdown(analysis.improved_prompt[:1200] + ("\n\n[dim]... (truncated for preview)[/dim]" if len(analysis.improved_prompt) > 1200 else "")),
        title="[bold green]Hardened Prompt Preview[/bold green]",
        border_style="green",
        subtitle="[dim]Check the export folder for the full version[/dim]"
    ))

    console.print(f"\n[bold green]✓ Done![/bold green] All artifacts (Report, Evals, Guardrails, Prompt) saved to:\n[underline cyan]{os.path.abspath(export_path)}[/underline cyan]")

if __name__ == "__main__":
    run()
