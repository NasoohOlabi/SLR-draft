# Enhancing Contextual Compatibility of Textual Steganography Systems Based on Large Language Models

This repository contains a systematic literature review on linguistic steganography with a focus on Large Language Models (LLMs).

## Project Structure

```
├── Enhancing Contextual Compatibility of Textual Steganography Systems Based on Large Language Models.tex  # Main LaTeX file
├── sections/                    # LaTeX section files and document class
│   ├── acmart.cls              # ACM document class
│   ├── introduction.tex        # Introduction section
│   ├── llm_approaches.tex      # Steganography and LLMs section
│   ├── study_design.tex        # Literature review methodology
│   ├── search_conducting.tex   # Search conducting section
│   ├── data_extraction.tex     # Data extraction section
│   ├── data_synthesis.tex      # Data synthesis section
│   ├── results_and_discussion.tex  # Results and discussion
│   ├── main_findings.tex       # Main findings section
│   ├── conclusion.tex          # Conclusion section
│   └── generated_tables.tex    # Generated tables
├── references/                 # Bibliography and reference materials
│   ├── bibliography.bib        # Bibliography file
│   ├── Reference SLR.pdf       # Reference SLR document
│   ├── Reference SLR.txt       # Reference SLR text
│   └── referencing instructions.md  # Referencing guidelines
├── data/                       # Data files
│   └── SLR - SLR-Deep.csv     # SLR data
├── scripts/                    # Python scripts for data processing
│   ├── generate_tables.py      # Table generation script
│   └── generate_sunburst.py    # Sunburst chart generation script
├── output/                     # Generated outputs and visualizations
│   ├── Enhancing Contextual Compatibility of Textual Steganography Systems Based on Large Language Models.pdf
│   ├── sunburst_chart.html     # Interactive sunburst chart
│   ├── sunburst_chart.pdf      # PDF version of sunburst chart
│   ├── sunburst_chart.png      # PNG version of sunburst chart
│   ├── treemap.png            # Treemap visualization
│   └── treemap.svg            # SVG version of treemap
└── build/                      # LaTeX build artifacts
    ├── *.aux                   # Auxiliary files
    ├── *.bbl                   # Bibliography files
    ├── *.fdb_latexmk          # LaTeX make database
    ├── *.fls                   # File list
    ├── *.log                   # Log files
    ├── *.out                   # Output files
    └── *.synctex.gz           # SyncTeX files
```

## Building the Document

To compile the LaTeX document:

```bash
pdflatex "Enhancing Contextual Compatibility of Textual Steganography Systems Based on Large Language Models.tex"
bibtex "Enhancing Contextual Compatibility of Textual Steganography Systems Based on Large Language Models"
pdflatex "Enhancing Contextual Compatibility of Textual Steganography Systems Based on Large Language Models.tex"
pdflatex "Enhancing Contextual Compatibility of Textual Steganography Systems Based on Large Language Models.tex"
```

## Data Processing

The `scripts/` directory contains Python scripts for:
- Generating tables from the SLR data
- Creating visualizations (sunburst charts, treemaps)

## Output Files

All generated outputs (PDF, visualizations) are stored in the `output/` directory for easy access and sharing.