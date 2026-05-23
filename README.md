# A Systematic Literature Review of LLM-Based Linguistic Steganography

This repository contains the LaTeX source, data, scripts, and generated outputs for a systematic literature review on large language models in linguistic steganography.

The paper focuses on contextual compatibility, evaluation challenges, and trade-offs in LLM-based steganographic methods.

## Repository Structure

```text
.
|-- draft.tex                 # Main LaTeX manuscript
|-- sections/                 # Section files and ACM class
|   |-- introduction.tex
|   |-- background.tex
|   |-- llm_approaches.tex
|   |-- related_reviews.tex
|   |-- research_method.tex
|   |-- results.tex
|   |-- discussion.tex
|   |-- threats.tex
|   |-- conclusion.tex
|   `-- generated_tables.tex
|-- references/               # Bibliography files and reference material
|-- data/                     # Source data used in the review
|-- scripts/                  # Python utilities for data processing and plotting
|-- output/                   # Generated figures and compiled PDF
`-- build/                    # LaTeX build artifacts
```

## Manuscript Overview

The manuscript reviews recent primary studies on:

- generative and rewriting-based LLM steganography
- black-box and context-aware approaches
- application domains and evaluation practices
- external knowledge integration
- recurring trade-offs in payload, naturalness, and security

## Building the Paper

Compile `draft.tex` with LaTeX and BibTeX:

```powershell
pdflatex draft.tex
bibtex draft
pdflatex draft.tex
pdflatex draft.tex
```

## Scripts

Key scripts in `scripts/`:

- `generate_tables.py` for table generation
- `generate_sunburst.py` for visualization
- `convert_scopus_to_bibtex.py` for bibliography conversion
- `clean_bibliography.py` for bibliography cleanup
- `verify_rq1_claims.py` for verification of RQ1-related claims

## Outputs

Generated figures and the compiled paper are stored in `output/`.
