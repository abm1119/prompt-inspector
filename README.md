# Prompt Inspector

<div align="center">
  <img src="src/inspector_ant.svg" width="160" height="160">
</div>

<div align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.136%2B-009688?logo=fastapi&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg">
  <img alt="LLM Ready" src="https://img.shields.io/badge/LLM-Groq%20Ready-8A2BE2">
</div>

Prompt Inspector is a simple, friendly tool that helps you test, improve, and understand AI prompts without needing technical expertise. You can paste a prompt, see what is strong or weak about it, make it safer and clearer, and export the result for later use.

---

## Why it matters

Prompt Inspector is built for anyone who wants better AI results without guesswork. It helps you turn a rough prompt into something clearer, safer, and more reliable in just a few steps.

## What this project does

Prompt Inspector helps you answer four simple questions about a prompt:

1. Is it easy to understand?
2. What parts are weak or risky?
3. How can it be improved?
4. Will it still work if the input is confusing or tricky?

It produces:
- structured prompt analysis
- quality and readability scores
- improved / hardened prompt versions
- vulnerability and guardrail recommendations
- adversarial stress-test results
- exportable reports and JSON artifacts

---

## Features at a glance

| Capability | What it gives you |
| :--- | :--- |
| Prompt analysis | Structural parsing, vulnerability detection, quality scoring |
| Prompt hardening | Safer, clearer, more reusable prompt rewrites |
| Stress testing | Adversarial variant evaluation and resilience checks |
| Export system | Markdown, JSON, guardrails, and manifest outputs |
| UI + CLI | Fast terminal workflow and polished browser dashboard |

## Core features

- Deep prompt classification and parsing
  - detects prompt types
  - extracts role, task, context, constraints, examples, goals
- Multi-metric quality scoring
  - grammar, clarity, specificity, structure, completeness, safety, robustness, reusability
  - readability heuristic (Flesch reading ease)
- Prompt hardening engine
  - rewrites prompts into more secure and structured versions
  - reinforces guardrails and task clarity
- Adversarial stress testing
  - simulates hostile, confusing, or malformed variants
  - identifies risk level and resilience observations
- Export system
  - markdown reports
  - JSON eval criteria
  - guardrails documents
  - manifest files
- Dual interface
  - rich terminal CLI
  - polished browser UI served by FastAPI

---

## Project structure

```text
prompt-inspector/
├── app.py                  # FastAPI app + web serving + API endpoints
├── main.py                 # CLI entry point
├── prompt.md               # prompt template / guidance notes
├── Prompt-Inspector-PRD.md # product requirements and roadmap notes
├── pyproject.toml          # project metadata and dependencies
├── src/
│   ├── analyzer.py         # prompt analysis and scoring
│   ├── cli.py              # rich terminal interface
│   ├── exporter.py         # export artifact generation
│   ├── improver.py         # score comparison and delta analysis
│   ├── models.py           # Pydantic models for analysis data
│   ├── stress_tester.py    # adversarial robustness testing
│   └── utils.py            # LLM utility wrapper and retry logic
├── web/
│   ├── index.html          # main frontend UI
│   ├── app.js              # result rendering / UI behavior
│   ├── styles.css          # premium visual theme and layout
│   └── inspector_ant.svg   # served logo asset
└── exports/                # generated output folders
```

---

## Requirements

- Python 3.11+
- A valid Groq API key
- Internet access for the LLM API calls

Recommended setup:
- `uv` for dependency management
- a virtual environment for isolated installs

---

## Quick start

### 0. Prerequisites

Before you begin, make sure you have:
- Python 3.11 or newer
- a working terminal
- a valid Groq API key

### 1. Clone the repository

```bash
git clone <your-repo-url>
pushd prompt-inspector
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install dependencies

Using `uv`:

```bash
uv sync
```

Or using pip:

```bash
pip install -r requirements.txt
```

> Note: `requirements.txt` is not currently present in this repository, so `uv sync` is the recommended path.

### 4. Add your API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_key_here
```

---

## Running the CLI

The CLI gives you a fast, high-signal workflow for prompt analysis, hardening, and export.

### Example

```bash
python main.py "Write a python script to scrape a website"
```

You can also pass longer prompts directly in quotes.

Expected flow:
1. analyze the original prompt
2. improve it with guardrails and structured formatting
3. stress-test the hardened prompt
4. save all artifacts into `exports/`

---

## Screenshot / preview

The web dashboard is designed to feel clean, minimal, and production-friendly. Once the app is running, open the local UI to inspect prompt analysis, quality scores, stress-test findings, and hardened prompt output in a single workspace.

### Part-1 Video

https://github.com/user-attachments/assets/9b58b35e-0491-45a5-95b1-1a7898da1d20

[Initial prompt processing - part 1](./demo/prompt-inspector-demo.mp4)

### Part-2 Video

https://github.com/user-attachments/assets/3f074c3f-05dd-484a-bc73-13d7d0f7c0b0

[Final Output - part 2](./demo/prompt-inspector%20demo_part2.mp4)

## Running the web UI

The FastAPI app serves the web interface and exposes the API endpoint used by the UI.

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000/
```

The UI includes:
- prompt input
- analysis and scoring tabs
- vulnerability review
- stress-test output
- hardened prompt preview
- export path access

---

## API endpoint

The main API endpoint is:

```http
POST /api/inspect
```

Request body:

```json
{
  "prompt": "Write a secure Python function that validates email addresses."
}
```

Response includes:
- `request_id`
- `export_path`
- `analysis`
- `comparison`
- `stress_results`

Example with `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/inspect \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a short welcome message for a new user."}'
```

---

## Output artifacts

Every run writes structured output into the `exports/` directory.

Typical output folder:

```text
exports/<task-name>-<timestamp>/
├── <task-name>.md
├── <task-name>-report.md
├── <task-name>-evals.json
├── <task-name>-guardrails.md
└── manifest.json
```

These files are useful for:
- review and documentation
- automated QA workflows
- prompt comparison and iteration
- sharing prompt hardening results with teammates

---

## How the analysis pipeline works

1. The prompt is submitted through the CLI or the web UI.
2. `src/analyzer.py` calls the LLM to extract structure, vulnerabilities, quality scores, and an improved prompt.
3. `src/improver.py` compares original vs improved scores to compute deltas.
4. `src/stress_tester.py` runs adversarial prompt variants against the hardened prompt.
5. `src/exporter.py` writes the results into `exports/`.

This gives you both a human-readable summary and machine-readable artifacts.

---

## Configuration notes

The app relies on the environment variable:

```env
GROQ_API_KEY=...
```

If the LLM call fails, the app will return clear runtime errors and the CLI will stop gracefully.

---

## Troubleshooting

### 405 Method Not Allowed on POST /api/inspect

This usually means the API route is being shadowed by the static file mount. Make sure the FastAPI app is started from the current codebase and that the route is defined before the catch-all static mount in `app.py`.

### Missing API key

If the model call fails, confirm that:
- `.env` exists in the project root
- `GROQ_API_KEY` is set correctly
- the environment is loaded before startup

### Export folder not appearing

Check that:
- the run completed successfully
- the app has write permissions for the `exports/` directory
- the prompt produced a valid analysis object

---

## Future improvements

Possible next enhancements:
- dashboard analytics and trend history
- richer dashboards and analytics trends
- saved prompt history and comparison views
- prompt templates and presets
- export to PDF / DOCX
- batch prompt analysis workflows

---

## License

MIT
