# AI Agent Collaboration Guide for the SLR on LLM-based Steganography

This document outlines how an AI assistant can effectively contribute to the development and refinement of this systematic literature review. The goal is to leverage AI capabilities to enhance the quality of the paper, streamline the workflow, and accelerate the research process.

## Project Overview

This project is a systematic literature review (SLR) on the use of Large Language Models (LLMs) in linguistic steganography. The paper is authored in LaTeX, with data analysis and visualization performed using Python scripts. The repository is well-structured, with clear separation of text, data, scripts, and generated outputs.

## How an AI Agent Can Help

An AI agent can assist in various aspects of this project. Here’s a breakdown of the key areas where AI collaboration can be most beneficial:

### 1. Writing and Editing

The agent can act as a writing partner to improve the clarity, flow, and academic rigor of the paper.

*   **Review and Refine:** Ask the agent to review paragraphs or sections for clarity, conciseness, and impact. For example: *"Review the introduction section and suggest improvements for a stronger opening."*
*   **Grammar and Style:** The agent can correct grammatical errors, improve sentence structure, and ensure a consistent academic tone.
*   **Citation Completion:** As highlighted in the `todo.md`, the paper has missing citations. The agent can help identify and format citations from the `references/` directory. For example: *"Find the correct citation for 'GPT-4' and add it to this sentence."*
*   **Summarization:** The agent can summarize long sections or even the entire paper to help refine the abstract and conclusion.

### 2. LaTeX Formatting

The agent can help troubleshoot and improve the LaTeX source code.

*   **Error Debugging:** If the document fails to compile, you can provide the LaTeX error log to the agent for debugging.
*   **Table and Figure Formatting:** The agent can help format tables and figures to meet the specific requirements of the `acmart` class. For example: *"Adjust the `generated_tables.tex` file to ensure the tables fit within the page margins."*
*   **Package Management:** The agent can suggest and implement LaTeX packages to add new features or improve formatting.

### 3. Data Analysis and Visualization

The agent can assist with the Python scripts used for data processing and visualization.

*   **Scripting Assistance:** Get help writing, debugging, or extending the Python scripts in the `scripts/` directory. For example: *"Modify `generate_sunburst.py` to use a different color scheme."*
*   **Data Interpretation:** The agent can help analyze the data in `data/` and interpret the results of the analysis, providing insights that can be incorporated into the paper.
*   **New Visualizations:** Request the agent to generate new plots or charts based on the SLR data to explore different facets of the research.

### 4. Bibliography Management

Maintaining a clean and accurate bibliography is crucial. The agent can help with this task.

*   **Clean .bib Files:** The agent can run the `scripts/clean_bibliography.py` script and help resolve any issues.
*   **Find Missing Information:** For incomplete references, the agent can search for missing details like DOIs, publication years, or conference names.

### 5. Verification and Review

The agent can help systematically address the items in the `todo.md` and `writing_improvements_summary.md` files.

*   **Run Verification Scripts:** The agent can execute scripts like `verify_rq1_claims.py` and provide a summary of the output.
*   **Address To-Do Items:** Assign specific tasks from the `todo.md` file to the agent. For example: *"Address the high-priority task 'Systematically Complete All Citations' from todo.md."*

### 6. Project Management

The agent can help manage the project workflow.

*   **Update `todo.md`:** The agent can update the to-do list based on the work completed.
*   **Summarize Progress:** Ask the agent for a summary of the recent changes and the overall progress of the project.

## Getting Started

To start collaborating with the AI agent, simply formulate your request in natural language. Be as specific as possible to get the best results. The agent has access to all the files in the repository and can read, write, and execute code.

By leveraging the capabilities of an AI assistant, we can significantly enhance the quality and impact of this research.

## Cursor Cloud specific instructions

This repo is an academic SLR manuscript (LaTeX) plus offline Python utilities — not a web/app service stack. There are no long-running application servers to start.

### Core workflows

- **Paper compile:** From repo root, follow README (`pdflatex` → `bibtex` → `pdflatex` ×2 on `draft.tex`). Output is `draft.pdf` (gitignored); a copy may already exist under `build/draft.pdf`.
- **Table regeneration:** `python3 scripts/generate_tables.py` (expects `./data/SLR - SLR-Deep.csv` and `./references/bibliography.bib`).
- **Bibliography cleanup:** `python3 scripts/clean_bibliography.py references/bibliography.bib`.
- **Sunburst chart:** `scripts/generate_sunburst.py` reads `./SLR - SLR-Deep.csv` in the **current working directory** (not `data/`). From repo root, symlink or copy `data/SLR - SLR-Deep.csv` before running, or `cd` appropriately.
- **Python deps:** `pandas`, `plotly`, `kaleido` (see `requirements.txt`). Optional: `openai` only for `scripts/filter_scopus_with_lmstudio.py` (needs a local/OpenAI-compatible API).

### Gotchas

- Several older scripts (`list_all_papers.py`, `analyze_*.py`) hardcode Windows paths (`d:\Master\...`); prefer scripts that use repo-relative paths (`generate_tables.py`, `clean_bibliography.py`, `convert_scopus_to_bibtex.py`).
- `verify_rq1_claims.py` expects `./SLR.xlsx` (not committed). Canonical coding data is the CSV under `data/`.
- ACM class is vendored at `sections/acmart.cls`; system TeX must provide `ACM-Reference-Format.bst` (texlive-publishers) and scalable fonts (`cm-super` / `lmodern`) or microtype font-expansion can abort PDF output.
- No conventional lint/test suite or package.json; “lint” is LaTeX compile + script dry-runs; “tests” are verification scripts like `verify_rq1_claims.py` when Excel data is available.
- `.gitignore` ignores `*.csv` and `draft.pdf`; tracked data under `data/` remains available via git.
