# Prompt Inspector v0.2.0

Advanced prompt validation, hardening, and adversarial stress testing engine.

## Features
- **Deep Analysis**: Classifies prompts and extracts key components (Role, Task, Constraints).
- **Quality Scoring**: Multi-dimensional scoring + heuristic readability (Flesch).
- **Hardening Engine**: Automatically rewrites prompts into structured, secure versions.
- **Adversarial Stress Testing**: Simulates attacks (injection, ambiguity) against the improved prompt.
- **Robustness**: Built-in retries, fallback models (Llama 3.3 70B -> Llama 3.1 8B), and JSON schema enforcement.
- **Comprehensive Artifacts**: Generates Reports, Guardrails, Evals, and Manifests.

## Setup
1. Clone the repository.
2. Install dependencies using `uv` or `pip`:
   ```bash
   uv sync
   # OR
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_key_here
   ```

## Usage
Run the inspector by passing a prompt as an argument or using the interactive mode:
```bash
python main.py "Write a python script to scrape a website"
```

## Architecture
- `src/analyzer.py`: Initial evaluation and improvement logic.
- `src/stress_tester.py`: Adversarial simulation engine.
- `src/improver.py`: Scoring delta analysis.
- `src/exporter.py`: Artifact generation.
- `src/utils.py`: Robust LLM client with retries and fallbacks.

## License
MIT
