import os
import json
import re
from datetime import datetime
from src.models import AnalysisResult, ComparisonReport

def slugify(text: str) -> str:
    return re.sub(r'[\W_]+', '-', text.lower()).strip('-')[:30]

def export_artifacts(original_prompt: str, analysis: AnalysisResult, comparison: ComparisonReport, stress_results: list):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name_slug = slugify(analysis.parsing.task or "prompt")
    folder = f"exports/{name_slug}-{timestamp}"
    os.makedirs(folder, exist_ok=True)

    # 1. Final Improved Prompt
    with open(f"{folder}/{name_slug}.md", "w", encoding="utf-8") as f:
        f.write(f"# Improved Prompt: {analysis.parsing.task or 'Untitled'}\n\n")
        f.write(analysis.improved_prompt)

    # 2. Comprehensive Report
    with open(f"{folder}/{name_slug}-report.md", "w", encoding="utf-8") as f:
        f.write(f"# Prompt Analysis Report\n\n")
        f.write(f"## Executive Summary\n")
        avg_orig = sum(v for k, v in analysis.scores.model_dump().items() if isinstance(v, (int, float)) and k != 'readability_score') / 8
        avg_imp = sum(v for k, v in comparison.improved_scores.model_dump().items() if isinstance(v, (int, float)) and k != 'readability_score') / 8
        f.write(f"- **Original Score:** {avg_orig:.1f}/100\n")
        f.write(f"- **Improved Score:** {avg_imp:.1f}/100\n")
        f.write(f"- **Readability (Flesch):** {comparison.improved_scores.readability_score:.1f}\n\n")
        
        f.write(f"## Original Prompt\n```markdown\n{original_prompt}\n```\n\n")
        f.write(f"## Classification\n**Types:** {', '.join(analysis.prompt_types)}\n\n")
        
        f.write(f"## Comparison Metrics\n")
        f.write("| Metric | Original | Improved | Delta |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for k, v in comparison.delta.items():
            f.write(f"| {k.capitalize()} | {comparison.original_scores.model_dump()[k]} | {comparison.improved_scores.model_dump()[k]} | {v:+} |\n")
        
        f.write(f"\n## Stress Test Results\n")
        f.write("| Variant Type | Status | Risk | Observation |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        for res in stress_results:
            status = "PASS" if res.passed else "FAIL"
            f.write(f"| {res.variant_type} | {status} | {res.risk_level} | {res.observation} |\n")

        f.write(f"\n## Vulnerabilities & Adversarial Variants\n")
        for v in analysis.vulnerabilities:
            f.write(f"- **Vuln:** {v}\n")
        
        f.write(f"\n### Stress Test Variants (Original Suggestions)\n")
        for var in analysis.adversarial_variants:
            f.write(f"#### {var.variant_type}\n")
            f.write(f"- **Content:** `{var.content}`\n")
            f.write(f"- **Potential Failure:** {var.failure_potential}\n")
            f.write(f"- **Mitigation:** {var.mitigation_strategy}\n\n")

    # 3. Evals JSON
    with open(f"{folder}/{name_slug}-evals.json", "w", encoding="utf-8") as f:
        json.dump([e.model_dump() for e in analysis.eval_criteria], f, indent=4)

    # 4. Guardrails
    with open(f"{folder}/{name_slug}-guardrails.md", "w", encoding="utf-8") as f:
        f.write("# Generated Guardrails\n\n")
        for g in analysis.suggested_guardrails:
            f.write(f"- {g}\n")

    # 5. Manifest
    manifest = {
        "timestamp": timestamp,
        "original_prompt": original_prompt,
        "analysis": analysis.model_dump(),
        "comparison": comparison.model_dump(),
        "stress_results": [r.model_dump() for r in stress_results]
    }
    with open(f"{folder}/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    return folder
