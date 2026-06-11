from typing import List, Dict
from src.models import QualityScores, ComparisonReport, AnalysisResult
from src.analyzer import evaluate_quality

def compare_scores(original: QualityScores, improved: QualityScores) -> ComparisonReport:
    orig_dict = original.model_dump()
    imp_dict = improved.model_dump()
    
    delta = {}
    key_improvements = []
    
    for key in orig_dict:
        if orig_dict[key] is not None and imp_dict[key] is not None:
            diff = imp_dict[key] - orig_dict[key]
            delta[key] = diff
            if diff > 10:
                key_improvements.append(f"Significant improvement in {key} (+{diff} points)")
            elif diff > 0:
                key_improvements.append(f"Minor improvement in {key} (+{diff} points)")
            elif diff < 0:
                key_improvements.append(f"Slight regression in {key} ({diff} points)")

    return ComparisonReport(
        original_scores=original,
        improved_scores=improved,
        delta=delta,
        key_improvements=key_improvements
    )

def run_improvement_cycle(prompt_text: str, analysis: AnalysisResult) -> ComparisonReport:
    """Evaluates the improved prompt and compares it to the original."""
    improved_prompt = analysis.improved_prompt
    improved_scores = evaluate_quality(improved_prompt)
    
    if not improved_scores:
        # Fallback if evaluation fails
        improved_scores = analysis.scores 
        
    return compare_scores(analysis.scores, improved_scores)
