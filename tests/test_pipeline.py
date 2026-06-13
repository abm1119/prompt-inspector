from src.improver import run_improvement_cycle
from src.models import AnalysisResult, QualityScores, PromptParsing


def test_run_improvement_cycle_uses_original_prompt_for_baseline(monkeypatch):
    original_scores = QualityScores(
        grammar=10,
        clarity=10,
        specificity=10,
        structure=10,
        completeness=10,
        safety=10,
        robustness=10,
        reusability=10,
    )
    improved_scores = QualityScores(
        grammar=20,
        clarity=20,
        specificity=20,
        structure=20,
        completeness=20,
        safety=20,
        robustness=20,
        reusability=20,
    )

    def fake_evaluate_quality(prompt_text):
        if prompt_text == "Original prompt":
            return original_scores
        return improved_scores

    monkeypatch.setattr("src.improver.evaluate_quality", fake_evaluate_quality)

    analysis = AnalysisResult(
        prompt_types=[],
        parsing=PromptParsing(),
        scores=QualityScores(
            grammar=0,
            clarity=0,
            specificity=0,
            structure=0,
            completeness=0,
            safety=0,
            robustness=0,
            reusability=0,
        ),
        vulnerabilities=[],
        suggested_guardrails=[],
        eval_criteria=[],
        improved_prompt="Improved prompt",
        adversarial_variants=[],
    )

    comparison = run_improvement_cycle("Original prompt", analysis)

    assert comparison.original_scores.grammar == 10
    assert comparison.improved_scores.grammar == 20
    assert comparison.delta["grammar"] == 10
