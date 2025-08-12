import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Configuration
csv_file_path = "SLR - SLR-Deep.csv"
# Change the output path to a PDF or SVG file
output_image_path = "sunburst_chart.pdf"  # Or "sunburst_chart.svg"
max_depth = 18

# Professional color palette
color_palette = [
    "#2E86AB",
    "#F6C85F",
    "#6B5B95",
    "#FF6F61",
    "#88B04B",
    "#955251",
    "#009B77",
    "#DD4124",
    "#D65076",
    "#45B8AC",
]

try:
    # Load and clean data
    df = pd.read_csv(csv_file_path)
    df = df[df["#"].notna() & (df["#"] <= max_depth)]

    if "title" not in df.columns or "Category" not in df.columns:
        raise ValueError("CSV must contain 'title' and 'Category' columns.")

    df["Category"] = df["Category"].fillna("N/A")
    df["title"] = df["title"].fillna("N/A")

    # --- NEW: Shorten Titles for Better Readability in the Chart ---
    df["display_title"] = df["title"].apply(
        lambda x: x if len(x) <= 20 else (x[:17] + "...")
    )
    # --- END NEW ---

    # Build labels and hierarchy
    labels = []
    parents = []
    color_map = {}
    color_ids = []

    for _, row in df.iterrows():
        cat = row["Category"]
        title = row["display_title"]  # Use the potentially shortened title for display

        if cat not in labels:
            labels.append(cat)
            parents.append("")
            color_map[cat] = color_palette[len(color_map) % len(color_palette)]
            color_ids.append(color_map[cat])

        labels.append(title)
        # labels.append("")
        parents.append(cat)
        color_ids.append(color_map[cat])

    # Create sunburst chart
    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            marker=dict(colors=color_ids),
            branchvalues="total",
            textinfo="label+text",  # Show labels directly on segments
            insidetextfont=dict(size=14, color="black"),
            outsidetextfont=dict(size=10, color="black"),
            # You can also add hovertemplate to show full title on hover if interactive PDF viewers are used
            # hovertemplate='<b>%{label}</b><br>%{parent}<br><extra></extra>'
        )
    )

    fig.update_layout(
        title_font=dict(size=24, family="Helvetica", color="black"),
        margin=dict(t=50, l=0, r=0, b=50),
        paper_bgcolor="white",
        # width=800, # Example width - uncomment and adjust if needed
        # height=800, # Example height - uncomment and adjust if needed
    )

    # Save image as PDF (or SVG)
    pio.write_image(fig, output_image_path)
    print(f"Sunburst chart saved to {output_image_path}")

except FileNotFoundError:
    print(f"File not found: {csv_file_path}")
except Exception as e:
    print(f"Error: {e}")
