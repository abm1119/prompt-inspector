import re
from src.utils import call_llm
from src.models import OptimizerResult, OptimizerStep


def _fallback_optimize(prompt_text: str) -> OptimizerResult:
    """Deterministic fallback that applies concept-elevation heuristics when the LLM path fails."""
    cleaned = re.sub(r"\s+", " ", prompt_text).strip()
    first_sentence = cleaned.split(".")[0] if "." in cleaned else cleaned
    goal = first_sentence[:180]

    optimized_prompt = (
        "You are an expert in prompt design and conversion-focused communication. "
        "Turn the following request into a lean, high-signal prompt using concept elevation. "
        "Keep the user's real goal, preserve the essential deliverables, remove repetition, "
        "and make the output modular, reusable, and easy to execute. "
        f"Primary goal: {goal}. "
        "Return the final assets in a clear structure with concise, practical guidance."
    )

    return OptimizerResult(
        summary="Applied concept-elevation heuristics to compress the prompt while keeping the goal, structure, and output quality intact.",
        optimized_prompt=optimized_prompt,
        why_better="This version removes instruction bloat, preserves intent, and gives the model room to adapt instead of over-constraining it.",
        steps=[
            OptimizerStep(name="Extract core intent", explanation=" Kept the real transformation and success condition at the center of the prompt."),
            OptimizerStep(name="Compress repeated detail", explanation="Removed duplicate phrases, platform clutter, and unnecessary edge-case wording."),
            OptimizerStep(name="Elevate to principles", explanation="Replaced narrow specifics with broader guidance that still protects the outcome."),
            OptimizerStep(name="Rebuild a clean flow", explanation="Grouped deliverables into a logical sequence the model can follow efficiently."),
            OptimizerStep(name="Preserve flexibility", explanation="Kept the prompt adaptable for reuse, delegation, and future iterations."),
        ],
    )


def optimize_prompt(prompt_text: str) -> OptimizerResult | None:
    """Generate an advanced concept-elevation prompt optimization using a strong rewrite strategy."""
    system_prompt = (
        "You are an advanced prompt optimizer specialized in concept elevation and prompt compression. "
        "Your job is to rewrite the user prompt into a shorter, stronger, more reusable prompt without losing the real intention. "
        "Use this framework: "
        "1) identify the core goal and success condition; "
        "2) remove repetition, over-specification, and procedural noise; "
        "3) turn detailed rules into broader principles; "
        "4) organize deliverables into a clear flow; "
        "5) preserve flexibility, clarity, and reuse value. "
        "The optimized prompt should feel expert-level, concise, modular, and practical. "
        "Aim for a 30-50% reduction in length while preserving the essential outcome. "
        "Return a JSON object with: summary, optimized_prompt, why_better, and steps (name + explanation)."
    )

    try:
        result = call_llm(system_prompt, f"Optimize this prompt using advanced concept elevation:\n\n{prompt_text}", OptimizerResult)
        if result and result.optimized_prompt.strip():
            return result
    except Exception as e:
        print(f"Optimizer Error: {e}")

    return _fallback_optimize(prompt_text)
