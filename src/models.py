from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class PromptParsing(BaseModel):
    role: Optional[str] = None
    task: Optional[str] = None
    context: Optional[str] = None
    constraints: List[str] = []
    output_format: Optional[str] = None
    examples: List[str] = []
    assumptions: List[str] = []

class QualityScores(BaseModel):
    grammar: float = Field(ge=0, le=100)
    clarity: float = Field(ge=0, le=100)
    specificity: float = Field(ge=0, le=100)
    structure: float = Field(ge=0, le=100)
    completeness: float = Field(ge=0, le=100)
    safety: float = Field(ge=0, le=100)
    robustness: float = Field(ge=0, le=100)
    reusability: float = Field(ge=0, le=100)
    readability_score: Optional[float] = None # Added for heuristic scoring

class AdversarialVariant(BaseModel):
    variant_type: str # e.g., "Prompt Injection", "Conflicting Instructions"
    content: str
    failure_potential: str # Description of why it might fail
    mitigation_strategy: str

class EvalCriterion(BaseModel):
    name: str
    description: str
    weight: float

class AnalysisResult(BaseModel):
    prompt_types: List[str]
    parsing: PromptParsing
    scores: QualityScores
    vulnerabilities: List[str]
    suggested_guardrails: List[str]
    eval_criteria: List[EvalCriterion]
    improved_prompt: str
    adversarial_variants: List[AdversarialVariant] = []

class ComparisonReport(BaseModel):
    original_scores: QualityScores
    improved_scores: QualityScores
    delta: Dict[str, float]
    key_improvements: List[str]
