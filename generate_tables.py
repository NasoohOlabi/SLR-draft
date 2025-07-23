import csv


def generate_latex_table(
    data, columns_to_display, caption, label, bib_data, column_mapping
):
    # Define column alignment: 'c' for Paper, 'p{3cm}' for others to enable wrapping
    column_width = "3cm"  # Fixed width for wrapping columns
    latex_code = (
        f"\\begin{{table*}}[htbp]\n\\centering\n\\caption{{{caption}}}\n\\label{{tab:{label}}}\n"
        f"\\resizebox{{0.8\\textwidth}}{{!}}{{\n\\fontsize{{3}}{{5}}\\selectfont\n\\begin{{tabular}}{{|c|{'|'.join(['p{' + column_width + '}'] * len(columns_to_display))}|}}\n\\hline\n"
    )

    # Generate header row without redundant "Number" column
    latex_code += (
        "Paper & "
        + " & ".join([col.replace("_", " ").title() for col in columns_to_display])
        + " \\\\\n\\hline\n"
    )

    for i, row in enumerate(data):
        if i >= 18:  # Limit to first 18 papers
            break

        # Map row data to named columns using the column_mapping
        mapped_row = {
            col_name: row[col_index] for col_name, col_index in column_mapping.items()
        }

        # Use paper number or citation key
        paper_id = str(mapped_row["number"])
        citation_key = ""
        for key, title in bib_data.items():
            if mapped_row["title"] in title:
                citation_key = key
                paper_id = f"\\cite{{{key}}}"
                break

        row_data = [paper_id]
        for col_name in columns_to_display:
            cell_content = mapped_row.get(col_name, "[Not specified]").strip()
            if not cell_content:  # Handle empty cells
                cell_content = "[Not specified]"

            # Replace specific Unicode and special characters with LaTeX equivalents
            # Delta variants
            cell_content = cell_content.replace("∆", "$\\Delta$")
            cell_content = cell_content.replace("Δ", "$\\Delta$")
            # Alpha variants
            cell_content = cell_content.replace("α", "$\\alpha$")
            # Epsilon variants (including mathematical italic)
            cell_content = cell_content.replace("𝜖", "$\\epsilon$")
            cell_content = cell_content.replace(
                "𝑒", "$\\epsilon$"
            )  # Additional variant check
            # Other Greek letters and symbols
            cell_content = cell_content.replace("μ", "$\\mu$")
            cell_content = cell_content.replace("∝", "$\\propto$")
            cell_content = cell_content.replace("τ", "$\\tau$")
            cell_content = cell_content.replace("θ", "$\\theta$")
            cell_content = cell_content.replace("̂", "\\textasciicircum{}")
            cell_content = cell_content.replace("∩", "$\\cap$")
            cell_content = cell_content.replace("≠", "$\\neq$")
            cell_content = cell_content.replace("~", "\\textasciitilde{}")
            cell_content = cell_content.replace("^", "\\textasciicircum{}")
            cell_content = cell_content.replace("\\", "\\textbackslash{}")
            # Escape LaTeX special characters (only outside math mode)
            cell_content = cell_content.replace("%", "\\%")
            cell_content = cell_content.replace("&", "\\&")
            cell_content = cell_content.replace("#", "\\#")
            # Underscores are safe in math mode; only escape in text
            if not cell_content.startswith("$") or not cell_content.endswith("$"):
                cell_content = cell_content.replace("_", "\\_")
            cell_content = cell_content.replace("{", "\\{")
            cell_content = cell_content.replace("}", "\\}")
            # Replace newlines with spaces
            cell_content = cell_content.replace("\n", " ")
            row_data.append(cell_content)

        latex_code += " & ".join(row_data) + " \\\\\n\\hline\n"

    latex_code += "\\end{tabular}\n}\n\\end{table*}\n\n"
    return latex_code


def parse_bib_file(bib_file_path):
    bib_data = {}
    with open(bib_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        entries = content.split("@")
        for entry in entries:
            if entry.strip():
                lines = entry.split("\n")
                entry_type_and_key = lines[0].strip()
                if "{" in entry_type_and_key:
                    key_start = entry_type_and_key.find("{") + 1
                    key_end = entry_type_and_key.find(",")
                    citation_key = entry_type_and_key[key_start:key_end].strip()

                    title_line = next(
                        (line for line in lines if "title=" in line), None
                    )
                    if title_line:
                        title_start = title_line.find("{") + 1
                        title_end = title_line.rfind("}")
                        title = title_line[title_start:title_end].strip()
                        bib_data[citation_key] = title
    return bib_data


# File paths
csv_file_path = "d:/Master/SLR draft/SLR - SLR-Deep.csv"
bib_file_path = "d:/Master/SLR draft/bibliography.bib"

# Parse bibliography
bib_data = parse_bib_file(bib_file_path)

# Read CSV data
all_data = []
with open(csv_file_path, "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if row:  # Ensure row is not empty
            all_data.append(row)

# Define column mapping from CSV index to meaningful names
column_mapping = {
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

# Define tables and their columns
tables_info = [
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

# Generate LaTeX tables
latex_output = ""
for table_info in tables_info:
    latex_output += generate_latex_table(
        all_data,
        table_info["columns"],
        table_info["caption"],
        table_info["label"],
        bib_data,
        column_mapping,
    )

# Write to file
with open("generated_tables.tex", "w", encoding="utf-8") as f:
    f.write(latex_output)

print("LaTeX tables generated successfully in generated_tables.tex")
