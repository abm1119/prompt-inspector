from pathlib import Path

from src.exporter import export_artifacts
from src.models import AnalysisResult, ComparisonReport, PromptParsing, QualityScores


def test_export_artifacts_formats_signed_score_deltas(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    original_scores = QualityScores(
        grammar=70,
        clarity=70,
        specificity=70,
        structure=70,
        completeness=70,
        safety=70,
        robustness=70,
        reusability=70,
    )
    improved_scores = QualityScores(
        grammar=85,
        clarity=85,
        specificity=85,
        structure=85,
        completeness=85,
        safety=85,
        robustness=85,
        reusability=85,
        readability_score=62,
    )
    analysis = AnalysisResult(
        prompt_types=["instructional"],
        parsing=PromptParsing(task="Inspect Prompt", role="Auditor"),
        scores=original_scores,
        vulnerabilities=[],
        suggested_guardrails=[],
        eval_criteria=[],
        improved_prompt="Improved prompt",
        adversarial_variants=[],
    )
    comparison = ComparisonReport(
        original_scores=original_scores,
        improved_scores=improved_scores,
        delta={"grammar": 15, "clarity": -2.5},
        key_improvements=["Clarified the task"],
    )

    folder = export_artifacts("Original prompt", analysis, comparison, [])

    report = Path(folder, "analysis-report.md").read_text(encoding="utf-8")
    assert "Delta: `+15.0`" in report
    assert "| Grammar | 70.0 | 85.0 | +15.0 |" in report
    assert "| Clarity | 70.0 | 85.0 | -2.5 |" in report
