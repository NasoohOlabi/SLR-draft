# -*- coding: utf-8 -*-

import pandas as pd
import re


TITLE_ALIASES = {
    # The CSV uses shortened working titles for these studies.
    "emotionally controllable steganography": "shi2025emotionally",
    "position agnostic generation": "lin2025positionagnostic",
    "two model defense repair": "chen2025activetwo",
}


def generate_latex_table(data, columns_to_display, caption, label, bib_data, column_mapping):
    """Generate a clean LaTeX longtable"""

    # Special character replacements
    replacements = {
        "∆": "\\ensuremath{\\Delta}",
        "Δ": "\\ensuremath{\\Delta}",
        "α": "\\ensuremath{\\alpha}",
        "μ": "\\ensuremath{\\mu}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
        "≈": "\\ensuremath{\\approx}",
        "≥": "\\ensuremath{\\geq}",
        "≤": "\\ensuremath{\\leq}",
        "±": "\\ensuremath{\\pm}",
        "×": "\\ensuremath{\\times}",
        "–": "--",
        "—": "---",
        "↓": "\\ensuremath{\\downarrow}",
        "↑": "\\ensuremath{\\uparrow}",
        "“": "``",
        "”": "''",
        "’": "'",
    }

    # Create column format with vertical lines - use appropriate widths that sum to less than 1.0
    num_cols = len(columns_to_display) + 1  # +1 for Paper column
    if num_cols == 2:
        col_format = "|p{0.3\\linewidth}|p{0.6\\linewidth}|"
    elif num_cols == 3:
        col_format = "|p{0.25\\linewidth}|p{0.35\\linewidth}|p{0.35\\linewidth}|"
    elif num_cols == 4:
        col_format = "|p{0.2\\linewidth}|p{0.25\\linewidth}|p{0.25\\linewidth}|p{0.25\\linewidth}|"
    elif num_cols == 7:
        # For 7 columns: Paper, LLM, Dataset, Result, Context Aware, Categ Context, Representation Context
        col_format = "|p{0.12\\linewidth}|p{0.12\\linewidth}|p{0.12\\linewidth}|p{0.18\\linewidth}|p{0.12\\linewidth}|p{0.12\\linewidth}|p{0.12\\linewidth}|"
    else:
        # For other cases, distribute evenly but keep under 0.9 total width
        col_width = 0.9 / num_cols
        col_specs = [f"p{{{col_width:.2f}\\linewidth}}"] * num_cols
        col_format = "|" + "|".join(col_specs) + "|"

    # Start table with proper longtable structure using hline for vertical line compatibility
    latex_code = (
        "\\renewcommand{\\arraystretch}{1.3}\n"
        f"\\begin{{longtable}}{{{col_format}}}\n"
        f"\\caption{{{caption}}} \\\\\n"
        "\\hline\n\n"
    )

    # Headers
    headers = ["Paper"] + [col.replace("_", " ").title()
                           for col in columns_to_display]
    latex_code += " & ".join(headers) + " \\\\\n"
    latex_code += "\\hline\n\n"
    latex_code += "\\endfirsthead\n\n"

    # Continuation header
    latex_code += (
        f"\\multicolumn{{{num_cols}}}{{|c|}}{{\\bfseries \\tablename\\ \\thetable{{}} -- continued from previous page}} \\\\\n"
        "\\hline\n"
        + " & ".join(headers) + " \\\\\n"
        "\\hline\n\n"
        "\\endhead\n\n"
    )

    # Footer
    latex_code += (
        f"\\hline\n"
        f"\\multicolumn{{{num_cols}}}{{|r|}}{{Continued on next page}} \\\\\n"
        "\\endfoot\n\n"
        "\\hline\n"
        "\\endlastfoot\n\n"
    )

    # Process data rows
    for i, row in enumerate(data):
        # Convert Excel values to strings, handling NaN
        mapped = {n: str(row[idx]) if idx < len(row) and pd.notna(row[idx]) else ""
                  for n, idx in column_mapping.items()}

        # Skip header row
        if mapped.get("number", "").lower() == "number":
            continue

        title_text = mapped.get("title", "").strip()
        if not title_text or title_text == "[Not specified]":
            continue

        if not mapped.get("Year", "").strip():
            continue

        paper_id = create_paper_citation(title_text, bib_data)

        # Build row with line breaks
        row_cells = [paper_id]
        for col in columns_to_display:
            cell_content = mapped.get(col, "[Not specified]").strip()
            if not cell_content:
                cell_content = "[Not specified]"
            cell_content = clean_latex_text(cell_content, replacements)
            row_cells.append(cell_content)

        # Add a horizontal rule after each row for clearer separation.
        latex_code += " & ".join(row_cells) + " \\\\\n\\hline\n\n"

    latex_code += "\\end{longtable}\n\n"
    return latex_code


def create_paper_citation(title_text, bib_data):
    """Create a proper paper citation"""
    # Try to find matching citation
    citation_key = None
    normalized_title = normalize_text(title_text)

    if normalized_title in TITLE_ALIASES:
        citation_key = TITLE_ALIASES[normalized_title]
    else:
        normalized_bib_titles = {
            key: normalize_text(bib_title) for key, bib_title in bib_data.items()
        }
        for key, bib_title in normalized_bib_titles.items():
            if normalized_title == bib_title or normalized_title in bib_title or bib_title in normalized_title:
                citation_key = key
                break

    # Truncate long titles and add citation
    if len(title_text) > 50:
        short_title = title_text[:47] + "..."
    else:
        short_title = title_text

    # Escape title text so special characters like '&' do not break table columns.
    short_title = clean_latex_text(short_title, {})

    if citation_key:
        return f"{short_title} \\cite{{{citation_key}}}"
    else:
        return short_title


def normalize_text(text):
    """Normalize text for tolerant title matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_latex_text(text, replacements):
    """Clean and escape text for LaTeX"""
    if not text or text == "[Not specified]":
        return "[Not specified]"

    # Handle special characters
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Clean up text
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space

    # Fix problematic LaTeX commands
    # Replace \textasc with [truncated]
    text = re.sub(r'\\textasc[^a-zA-Z]*', '[truncated]', text)

    # Escape LaTeX special characters
    text = re.sub(r"(?<!\\)&", r"\\&", text)
    text = re.sub(r"(?<!\\)%", r"\\%", text)
    text = re.sub(r"(?<!\\)#", r"\\#", text)
    text = re.sub(r"(?<!\\)_", r"\\_", text)

    # Remove diacritical marks
    text = re.sub(r"[\u0300-\u036f]", "", text)

    # Truncate very long content
    if len(text) > 150:
        text = text[:147] + "..."

    return text.strip()


def extract_bib_field(entry, field_name):
    """Extract a BibTeX field value while handling nested braces."""
    field_match = re.search(rf"\b{re.escape(field_name)}\s*=\s*", entry, re.IGNORECASE)
    if not field_match:
        return None

    idx = field_match.end()
    while idx < len(entry) and entry[idx].isspace():
        idx += 1
    if idx >= len(entry):
        return None

    delimiter = entry[idx]
    if delimiter == "{":
        depth = 0
        start = idx + 1
        for pos in range(idx, len(entry)):
            char = entry[pos]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return entry[start:pos].strip()
    elif delimiter == "\"":
        start = idx + 1
        escaped = False
        for pos in range(start, len(entry)):
            char = entry[pos]
            if char == "\"" and not escaped:
                return entry[start:pos].strip()
            escaped = (char == "\\") and not escaped

    return None


def parse_bib_file(path):
    """Parse bibliography file to extract citation keys and titles"""
    bib = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        for entry in content.split("@")[1:]:
            lines = entry.split("\n")
            if not lines:
                continue

            header = lines[0]
            if "{" in header:
                key = header.split("{", 1)[1].split(",", 1)[0].strip()
                title = extract_bib_field(entry, "title")
                if title:
                    bib[key] = " ".join(title.split())
    except FileNotFoundError:
        print(f"Warning: Bibliography file not found at {path}")
    except Exception as e:
        print(f"Warning: Error parsing bibliography file: {e}")

    return bib


if __name__ == "__main__":
    # Paths - use relative paths
    csv_path = "./data/SLR - SLR-Deep.csv"
    bib_path = "./references/bibliography.bib"

    try:
        # Read data from canonical CSV file
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        # Convert DataFrame to list of lists format (headers + data rows)
        rows = [df.columns.tolist()] + df.values.tolist()

        headers, data_rows = rows[0], rows[1:]
        bib = parse_bib_file(bib_path)
        # Handle Excel numeric types (may be float/NaN) when sorting
        data_rows.sort(key=lambda x: int(float(x[0])) if pd.notna(
            x[0]) and str(x[0]).strip() else 0)

        cmap = {name: idx for idx, name in enumerate(headers)}
        cmap["number"] = cmap.get("#", 0)

        # Define tables to generate
        tables = [
            {
                "env": "table*",
                "name": "results",
                "columns": ["LLM", "Year", "dataset", "result", "context aware",
                            "categ context",
                            "representation context",],
                "caption": "Summary of Results from Reviewed Papers",
                "label": "results_summary",
            },
        ]

        # Generate tables
        output_content = ""
        for table_config in tables:
            output_content += generate_latex_table(
                data_rows,
                table_config["columns"],
                table_config["caption"],
                table_config["label"],
                bib,
                cmap
            )

        # Write to file
        with open("./sections/generated_tables.tex", "w", encoding="utf-8") as fo:
            fo.write(output_content)
        print("Successfully wrote generated_tables.tex")

    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        print(
            "Please ensure the CSV file and bibliography file exist in the correct locations.")
    except Exception as e:
        print(f"Error generating tables: {e}")
