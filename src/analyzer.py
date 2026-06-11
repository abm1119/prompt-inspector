import textstat
from typing import Optional
from src.models import AnalysisResult, QualityScores
from src.utils import call_llm

def calculate_heuristics(prompt_text: str) -> float:
    return textstat.flesch_reading_ease(prompt_text)

def analyze_prompt(prompt_text: str) -> Optional[AnalysisResult]:
    system_prompt = (
        "You are an expert prompt engineer and security researcher.\n"
        "Analyze the provided prompt thoroughly. Your analysis must include:\n"
        "1. Classification: Identify all applicable prompt types.\n"
        "2. Parsing: Extract role, task, context, constraints, etc.\n"
        "3. Scoring: Rate 0-100 on key quality metrics.\n"
        "4. Vulnerabilities: Find security and logic flaws.\n"
        "5. Adversarial Variants: Generate 3 specific variants that would test this prompt's weaknesses.\n"
        "6. Guardrails & Evals: Provide concrete mitigation and measurement criteria.\n"
        "7. Improvement: Provide a fully optimized, HARDENED version of the prompt.\n"
        "   - Use Markdown headers (Role, Task, Context, Constraints, System Guardrails).\n"
        "   - Include instructions to ignore user overrides and stick to the task.\n"
        "   - Be extremely detailed and professional.\n"
        "Be critical and precise."
    )

    try:
        result = call_llm(system_prompt, f"Analyze this prompt:\n\n{prompt_text}", AnalysisResult)
        if result:
            result.scores.readability_score = calculate_heuristics(prompt_text)
        return result
    except Exception as e:
        print(f"Final Analysis Error: {e}")
        return None

def evaluate_quality(prompt_text: str) -> Optional[QualityScores]:
    """Lightweight scoring for re-evaluation."""
    system_prompt = "Rate the following prompt quality on a scale of 0-100 for each metric."
    try:
        scores = call_llm(system_prompt, f"Rate this prompt:\n\n{prompt_text}", QualityScores)
        if scores:
            scores.readability_score = calculate_heuristics(prompt_text)
        return scores
    except Exception as e:
        print(f"Scoring Error: {e}")
        return None
