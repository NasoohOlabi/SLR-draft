# -*- coding: utf-8 -*-

import pandas as pd
import re


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
        # Handle Excel numeric types and NaN values
        first_val = row[0] if len(row) > 0 else None
        if first_val is not None and pd.notna(first_val) and str(first_val).strip():
            try:
                if int(float(first_val)) >= 25:
                    print(row)
                    continue
            except (ValueError, TypeError):
                pass

        # Convert Excel values to strings, handling NaN
        mapped = {n: str(row[idx]) if idx < len(row) and pd.notna(row[idx]) else ""
                  for n, idx in column_mapping.items()}

        # Skip header row
        if mapped.get("number", "").lower() == "number":
            continue

        title_text = mapped.get("title", "").strip()
        if not title_text or title_text == "[Not specified]":
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

        # add blank line after each row
        latex_code += " & ".join(row_cells) + " \\\\\n\n"

    latex_code += "\\end{longtable}\n\n"
    return latex_code


def create_paper_citation(title_text, bib_data):
    """Create a proper paper citation"""
    # Try to find matching citation
    citation_key = None
    for key, bib_title in bib_data.items():
        if title_text.lower() in bib_title.lower() or bib_title.lower() in title_text.lower():
            citation_key = key
            break

    # Truncate long titles and add citation
    if len(title_text) > 50:
        short_title = title_text[:47] + "..."
    else:
        short_title = title_text

    if citation_key:
        return f"{short_title} \\cite{{{citation_key}}}"
    else:
        return short_title


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

                # Look for title
                for line in lines[1:]:
                    if "title=" in line.lower():
                        # Extract title between braces
                        title_match = re.search(
                            r'title\s*=\s*\{([^}]+)\}', line, re.IGNORECASE)
                        if title_match:
                            title = title_match.group(1).strip()
                            bib[key] = title
                            break
    except FileNotFoundError:
        print(f"Warning: Bibliography file not found at {path}")
    except Exception as e:
        print(f"Warning: Error parsing bibliography file: {e}")

    return bib


if __name__ == "__main__":
    # Paths - use relative paths
    excel_path = "./SLR.xlsx"
    bib_path = "./references/bibliography.bib"

    try:
        # Read data from Excel file
        df = pd.read_excel(excel_path, sheet_name="SLR-Deep")
        # Convert DataFrame to list of lists format (headers + data rows)
        rows = [df.columns.tolist()] + df.values.tolist()

        headers, data_rows = rows[0], rows[1:]
        bib = parse_bib_file(bib_path)
        # Handle Excel numeric types (may be float/NaN) when sorting
        data_rows.sort(key=lambda x: int(float(x[0])) if pd.notna(
            x[0]) and str(x[0]).strip() else 0)

        # Column mapping - adjust indices based on actual CSV structure
        cmap = {
            "number": 0,
            "title": 1,
            "Year": 2,
            "Type": 3,
            "LLM": 5,
            "dataset": 9,
            "result": 12,
            "Main strengths": 7,
            "Main weaknesses": 8,
            "pipline method used": 14,
            "context aware": 15,
            "categ context": 16,
            "representation context": 17,
            "context usage in method detail text": 18,
        }

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
            "Please ensure the Excel file and bibliography file exist in the correct locations.")
    except Exception as e:
        print(f"Error generating tables: {e}")
