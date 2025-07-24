import csv
import re


def generate_latex_table(
    data, columns_to_display, caption, label, bib_data, column_mapping
):
    # Define replacements for special symbols (uses ensuremath for safe math mode)
    specific_replacements = {
        "∆": r"\ensuremath{\Delta}",
        "Δ": r"\ensuremath{\Delta}",
        "α": r"\ensuremath{\alpha}",
        "𝜖": r"\ensuremath{\epsilon}",
        "𝑒": r"\ensuremath{\epsilon}",
        "μ": r"\ensuremath{\mu}",
        "∝": r"\ensuremath{\propto}",
        "τ": r"\ensuremath{\tau}",
        "θ": r"\ensuremath{\theta}",
        "∩": r"\ensuremath{\cap}",
        "≠": r"\ensuremath{\neq}",
    }

    # Use single-column table environment
    env = "table"
    # Compute column format
    col_format = "|c|" + "|X|" * len(columns_to_display)

    # Begin LaTeX table
    latex_code = (
        f"\\begin{{{env}}}[htbp]\n"
        f"\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{tab:{label}}}\n"
        f"\\small\n"
        f"\\begin{{tabularx}}{{\\linewidth}}{{{col_format}}}\n"
        f"\\hline\n"
    )

    # Header
    headers = ["Paper"] + [col.replace("_", " ").title() for col in columns_to_display]
    latex_code += " & ".join(headers) + r" \\\hline" + "\n"

    # Rows
    for i, row in enumerate(data):
        if i >= 18:
            break
        mapped = {n: row[idx] for n, idx in column_mapping.items()}
        if mapped.get("number", "").lower() == "number":
            continue
        title_text = mapped.get("title", "").strip()
        pid = mapped.get("number", "").strip()
        if title_text:
            for key, title in bib_data.items():
                if title_text == title:
                    pid = f"\\cite{{{key}}}"
                    break
        cells = [pid]
        for col in columns_to_display:
            cell = mapped.get(col, "[Not specified]").strip() or "[Not specified]"
            tags = {}
            for j, (char, sym) in enumerate(specific_replacements.items()):
                tag = f"PH{j}TAG"
                tags[tag] = sym
                cell = cell.replace(char, tag)
            cell = cell.replace("\n", " ")
            cell = re.sub(r"(?<!\\)&", r"\\&", cell)
            cell = re.sub(r"(?<!\\)%", r"\\%", cell)
            cell = re.sub(r"(?<!\\)#", r"\\#", cell)
            cell = re.sub(r"(?<!\\)_", r"\\_", cell)
            # remove stray combining diacritics
            cell = re.sub(r"[\u0300-\u036f]", "", cell)

            # now escape carets so they don’t break in text mode
            cell = re.sub(r"(?<!\\)\^", r"\\^{}", cell)
            # finally restore any special‐symbol tags
            for tag, sym in tags.items():
                cell = cell.replace(tag, sym)

            for tag, sym in tags.items():
                cell = cell.replace(tag, sym)
            cells.append(cell)
        if len(cells) != len(headers):
            raise ValueError(f"Row {i} has {len(cells)} cells; expected {len(headers)}")
        latex_code += " & ".join(cells) + r" \\\hline" + "\n"

    # End environments
    latex_code += f"\\end{{tabularx}}\n\\end{{{env}}}\n\n"
    return latex_code


def parse_bib_file(path):
    bib = {}
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for entry in content.split("@")[1:]:
        hdr, *lns = entry.split("\n")
        if "{" in hdr:
            key = hdr.split("{", 1)[1].split(",", 1)[0].strip()
            for l in lns:
                if "title=" in l:
                    t = l.split("{", 1)[1].rsplit("}", 1)[0].strip()
                    bib[key] = t
                    break
    return bib


if __name__ == "__main__":
    # Paths
    csv_path = "d:/Master/SLR draft/SLR - SLR-Deep.csv"
    bib_path = "d:/Master/SLR draft/bibliography.bib"
    # Read data
    with open(csv_path, "r", encoding="utf-8") as cf:
        rows = [r for r in csv.reader(cf) if r]
    headers, data_rows = rows[0], rows[1:]
    bib = parse_bib_file(bib_path)
    # Mapping
    cmap = {
        "number": 0,
        "title": 1,
        "Type": 2,
        "LLM": 5,
        "dataset": 10,
        "result": 13,
        "Main strengths": 8,
        "Main weaknesses": 9,
        "pipline method used": 15,
        "context aware": 16,
        "categ context": 17,
        "representation context": 18,
        "context usage in method detail text": 19,
    }
    tables = [
        {
            "name": "results",
            "columns": ["result"],
            "caption": "Summary of Results from Reviewed Papers",
            "label": "results_summary",
        },
        {
            "name": "model_dataset",
            "columns": ["LLM", "dataset"],
            "caption": "Models and Datasets Used in Reviewed Papers",
            "label": "models_datasets",
        },
        {
            "name": "context_fields",
            "columns": [
                "context aware",
                "categ context",
                "representation context",
                "context usage in method detail text",
            ],
            "caption": "Context-Related Fields in Reviewed Papers",
            "label": "context_fields",
        },
        {
            "name": "category_strengths_weaknesses",
            "columns": ["Type", "Main strengths", "Main weaknesses"],
            "caption": "Categories, Main Strengths, and Weaknesses of Reviewed Papers",
            "label": "category_strengths_weaknesses",
        },
        {
            "name": "approach",
            "columns": ["pipline method used"],
            "caption": "Approach/Pipeline Method Used in Reviewed Papers",
            "label": "approach_method",
        },
    ]
    # Generate and write
    out = "".join(
        generate_latex_table(
            data_rows, t["columns"], t["caption"], t["label"], bib, cmap
        )
        for t in tables
    )
    with open("generated_tables.tex", "w", encoding="utf-8") as fo:
        fo.write(out)
    print("Wrote generated_tables.tex")
