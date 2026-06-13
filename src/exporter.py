import os
import json
import re
from datetime import datetime
from src.models import AnalysisResult, ComparisonReport

def slugify(text: str) -> str:
    """Creates a URL-friendly slug from text."""
    return re.sub(r'[\W_]+', '-', text.lower()).strip('-')[:40]

def format_score(val) -> str:
    """Formats a score as a string with one decimal place."""
    try:
        return f"{float(val):.1f}"
    except (ValueError, TypeError):
        return "N/A"

def export_artifacts(original_prompt: str, analysis: AnalysisResult, comparison: ComparisonReport, stress_results: list):
    """
    Exports the analysis results into a premium, well-structured folder of artifacts.
    Includes: Hardened Prompt, Comprehensive Report, Evals, Guardrails, and Manifest.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    task_name = analysis.parsing.task or "prompt-analysis"
    name_slug = slugify(task_name)
    folder = f"exports/{name_slug}-{timestamp}"
    os.makedirs(folder, exist_ok=True)

    # 1. Final Improved (Hardened) Prompt
    # Uses frontmatter for metadata richness
    with open(f"{folder}/hardened-prompt.md", "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"title: Hardened Prompt - {task_name}\n")
        f.write(f"date: {datetime.now().isoformat()}\n")
        f.write(f"role: {analysis.parsing.role or 'N/A'}\n")
        f.write(f"types: {', '.join(analysis.prompt_types)}\n")
        f.write("---\n\n")
        f.write(f"# {task_name}\n\n")
        f.write("> This prompt has been structurally hardened and optimized for clarity, safety, and performance.\n\n")
        f.write("## The Prompt\n\n")
        f.write("```markdown\n")
        f.write(analysis.improved_prompt)
        f.write("\n```\n")

    # 2. Comprehensive Analysis Report
    # Professional layout with clear sections and high-signal data representation
    with open(f"{folder}/analysis-report.md", "w", encoding="utf-8") as f:
        f.write(f"# Prompt Analysis Report: {task_name}\n\n")
        
        f.write("## 1. Executive Summary\n")
        f.write("---\n")
        avg_orig = sum(v for k, v in analysis.scores.model_dump().items() if isinstance(v, (int, float)) and k != 'readability_score') / 8
        avg_imp = sum(v for k, v in comparison.improved_scores.model_dump().items() if isinstance(v, (int, float)) and k != 'readability_score') / 8
        
        f.write(f"- **Final Hardened Score:** `{format_score(avg_imp)}/100` (Delta: `{format_score(avg_imp - avg_orig):+}`)\n")
        f.write(f"- **Readability (Flesch):** `{format_score(comparison.improved_scores.readability_score)}`\n")
        f.write(f"- **Status:** {'✅ Stable & Optimized' if avg_imp > 80 else '⚠️ Needs Further Review'}\n\n")
        
        f.write("### Key Improvements\n")
        for imp in comparison.key_improvements:
            f.write(f"- {imp}\n")
        f.write("\n")

        f.write("## 2. Structural Decomposition\n")
        f.write("---\n")
        f.write(f"| Component | Analysis |\n")
        f.write(f"| :--- | :--- |\n")
        f.write(f"| **Assigned Role** | {analysis.parsing.role or 'Generic'} |\n")
        f.write(f"| **Primary Task** | {analysis.parsing.task or 'N/A'} |\n")
        f.write(f"| **Output Format** | {analysis.parsing.output_format or 'Auto'} |\n")
        f.write(f"| **Prompt Types** | {', '.join(analysis.prompt_types)} |\n\n")

        f.write("### Constraints & Guardrails\n")
        for c in analysis.parsing.constraints:
            f.write(f"- {c}\n")
        f.write("\n")

        f.write("## 3. Comparative Metrics\n")
        f.write("---\n")
        f.write("| Quality Dimension | Original | Hardened | Delta |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for k, v in comparison.delta.items():
            f.write(f"| {k.replace('_',' ').capitalize()} | {format_score(comparison.original_scores.model_dump()[k])} | {format_score(comparison.improved_scores.model_dump()[k])} | {v:+} |\n")
        f.write("\n")

        f.write("## 4. Stress Test Results\n")
        f.write("---\n")
        f.write("> Empirical verification of prompt robustness against adversarial attack vectors.\n\n")
        f.write("| Vector | Status | Risk Level | Observation |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        for res in stress_results:
            status = "✅ PASS" if res.passed else "❌ FAIL"
            f.write(f"| {res.variant_type} | {status} | {res.risk_level.upper()} | {res.observation} |\n")
        f.write("\n")

        f.write("## 5. Vulnerability Assessment\n")
        f.write("---\n")
        if analysis.vulnerabilities:
            for v in analysis.vulnerabilities:
                f.write(f"- ⚠️ **Critical Finding:** {v}\n")
        else:
            f.write("- No critical structural vulnerabilities detected.\n")
        f.write("\n")

        f.write("## 6. Original Source\n")
        f.write("---\n")
        f.write("```markdown\n")
        f.write(original_prompt)
        f.write("\n```\n")

    # 3. Evaluation Criteria (JSON)
    with open(f"{folder}/eval-criteria.json", "w", encoding="utf-8") as f:
        json.dump([e.model_dump() for e in analysis.eval_criteria], f, indent=4)

    # 4. Guardrails (Markdown)
    with open(f"{folder}/suggested-guardrails.md", "w", encoding="utf-8") as f:
        f.write(f"# Hardened Guardrails: {task_name}\n\n")
        f.write("> Copy these into your system instructions to maintain output integrity.\n\n")
        for g in analysis.suggested_guardrails:
            f.write(f"- {g}\n")

    # 5. Full Manifest (JSON)
    manifest = {
        "metadata": {
            "version": "1.2.0",
            "timestamp": timestamp,
            "task": task_name,
            "slug": name_slug
        },
        "original_prompt": original_prompt,
        "analysis": analysis.model_dump(),
        "comparison": comparison.model_dump(),
        "stress_results": [r.model_dump() for r in stress_results]
    }
    with open(f"{folder}/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    return folder
