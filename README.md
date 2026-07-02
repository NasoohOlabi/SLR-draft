# SLR Draft: LLM-Based Linguistic Steganography

This repository contains the LaTeX source for a systematic literature review on LLM-based linguistic steganography, focused on contextual compatibility, evaluation challenges, and trade-offs.

## Current Layout

```text
draft.tex                 Main IEEE Access manuscript
sections/                 Manuscript sections and generated tables
references/bibliography.bib
                          Active BibTeX database
ieeeaccess.cls            IEEE Access class used by draft.tex
IEEEtran.bst              IEEE bibliography style
IEEEtran.cls              IEEE class reference asset
*.pfb, *.tfm, *.fd, *.map  Font assets required by the IEEE Access class
logo.png, notaglinelogo.png, bullet.png, spotcolor.sty
                          IEEE Access template assets
```

Generated files such as `draft.pdf`, `.aux`, `.bbl`, `.log`, `build/`, and `output/` are intentionally ignored.

## Build

Run from the repository root:

```powershell
pdflatex draft.tex
bibtex draft
pdflatex draft.tex
pdflatex draft.tex
```

The manuscript now uses `ieeeaccess.cls` and `IEEEtran.bst`.

## Cleanup Notes

The repository has been narrowed to the active manuscript source, bibliography, and IEEE template assets. Older review notes, prior PDFs, generated visualizations, raw CSV exports, and helper scripts were removed from version control because they are not required to build the current paper.
