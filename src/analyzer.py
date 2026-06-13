import textstat
from typing import Optional
from src.models import AnalysisResult, QualityScores
from src.utils import call_llm

def calculate_heuristics(prompt_text: str) -> float:
    readability_fn = getattr(textstat, "flesch_reading_ease", None)
    if callable(readability_fn):
        score = readability_fn(prompt_text)
        return float(score) if isinstance(score, (int, float)) else 0.0
    return 0.0

def analyze_prompt(prompt_text: str) -> Optional[AnalysisResult]:
    system_prompt = (
        "You are an expert prompt engineer and security researcher specializing in high-performance LLM orchestration.\n"
        "Analyze the provided prompt thoroughly. Your analysis must include:\n"
        "1. Classification: Identify all applicable prompt types (e.g., Few-shot, Chain-of-Thought, Meta-prompting).\n"
        "2. Parsing: Extract the semantic core: role, task, context, constraints, output format, examples, and assumptions.\n"
        "3. Scoring: Rate 0-100 on quality dimensions (Clarity, Specificity, Structure, etc.).\n"
        "4. Vulnerabilities: Identify structural weaknesses, logical fallacies, and security risks (injection, leakage).\n"
        "5. Adversarial Variants: Generate 3 specific stress-test variants.\n"
        "6. Guardrails & Evals: Provide concrete mitigation rules and objective measurement criteria.\n"
        "7. Improvement: Provide a fully optimized, PREMIUM HARDENED version of the prompt.\n"
        "   - Use a clear, sophisticated structure (e.g., # Role, # Context, # Instructions, # Constraints, # Safety).\n"
        "   - Use high-signal language. Be explicit, not suggestive.\n"
        "   - Include 'System-level Guardrails' to prevent instruction override.\n"
        "   - Ensure the final output is ready for production use in high-stakes environments.\n"
        "Your output must be precise, professional, and represent the absolute state-of-the-art in prompt engineering."
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
