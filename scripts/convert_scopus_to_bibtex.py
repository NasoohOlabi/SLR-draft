#!/usr/bin/env python3
"""Convert a merged Scopus JSON export into BibTeX.

The script is designed for Parsif.al import: it keeps the output simple,
uses standard BibTeX entry types, and tries to preserve the most useful
metadata from Scopus records.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


TYPE_MAP = {
    "Article": "article",
    "Review": "article",
    "Short Survey": "article",
    "Letter": "article",
    "Note": "article",
    "Editorial": "article",
    "Conference Paper": "inproceedings",
    "Conference Review": "inproceedings",
    "Book Chapter": "incollection",
    "Book": "book",
}


def load_scopus_entries(input_path: Path) -> List[Dict[str, Any]]:
    with input_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    entries = data.get("search-results", {}).get("entry", [])
    if not isinstance(entries, list):
        raise ValueError("Expected search-results.entry to be a list")
    return entries


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    escaped = value
    for old, new in replacements.items():
        escaped = escaped.replace(old, new)
    return escaped


def ascii_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^A-Za-z0-9]+", "", normalized)
    return normalized


def format_author_name(raw_name: str) -> str:
    raw_name = raw_name.strip()
    if not raw_name:
        return ""

    if "," in raw_name:
        last, first = [part.strip() for part in raw_name.split(",", 1)]
        return f"{last}, {first}"

    tokens = raw_name.split()
    if len(tokens) == 1:
        return tokens[0]

    surname = tokens[0]
    given_tokens = tokens[1:]
    initials: List[str] = []
    for token in given_tokens:
        cleaned = token.replace(".", "")
        if cleaned and all(ch.isalpha() for ch in cleaned):
            initials.extend(list(cleaned))
        else:
            initials.append(token)
    formatted_given = " ".join(
        f"{token}." if len(token) == 1 and token.isalpha() else token for token in initials
    )
    return f"{surname}, {formatted_given}".strip()


def format_authors(raw_creator: Any) -> str:
    if not raw_creator:
        return ""

    if isinstance(raw_creator, list):
        authors = [format_author_name(str(item)) for item in raw_creator if str(item).strip()]
    else:
        creator = str(raw_creator)
        parts = re.split(r"\s+and\s+|;\s*|\s*&\s*", creator)
        authors = [format_author_name(part) for part in parts if part.strip()]

    return " and ".join(author for author in authors if author)


def get_year(entry: Dict[str, Any]) -> str:
    cover_date = str(entry.get("prism:coverDate") or "").strip()
    if len(cover_date) >= 4 and cover_date[:4].isdigit():
        return cover_date[:4]

    year = str(entry.get("prism:publicationDate") or "").strip()
    if len(year) >= 4 and year[:4].isdigit():
        return year[:4]

    return "n.d."


def get_pages(entry: Dict[str, Any]) -> str:
    page_range = entry.get("prism:pageRange")
    if page_range:
        pages = str(page_range).strip()
        return pages.replace("-", "--")

    article_number = entry.get("article-number")
    if article_number:
        return str(article_number).strip()

    return ""


def get_entry_type(entry: Dict[str, Any]) -> str:
    subtype = str(entry.get("subtypeDescription") or "").strip()
    return TYPE_MAP.get(subtype, "article")


def get_entry_fields(entry: Dict[str, Any], bib_type: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}

    title = str(entry.get("dc:title") or "").strip()
    if title:
        fields["title"] = latex_escape(title)

    authors = format_authors(entry.get("dc:creator"))
    if authors:
        fields["author"] = authors

    publication_name = str(entry.get("prism:publicationName") or "").strip()
    if publication_name:
        if bib_type == "article":
            fields["journal"] = latex_escape(publication_name)
        elif bib_type == "book":
            fields["publisher"] = latex_escape(publication_name)
        else:
            fields["booktitle"] = latex_escape(publication_name)

    volume = str(entry.get("prism:volume") or "").strip()
    if volume:
        fields["volume"] = volume

    issue = str(entry.get("prism:issueIdentifier") or "").strip()
    if issue:
        fields["number"] = issue

    pages = get_pages(entry)
    if pages:
        fields["pages"] = pages

    doi = str(entry.get("prism:doi") or "").strip()
    if doi:
        fields["doi"] = doi
        fields["url"] = f"https://doi.org/{doi}"

    issn = str(entry.get("prism:issn") or entry.get("prism:eIssn") or "").strip()
    if issn and bib_type == "article":
        fields["issn"] = issn

    return fields


def entry_sort_key(entry: Dict[str, Any]) -> Tuple[str, str, str]:
    year = get_year(entry)
    title = str(entry.get("dc:title") or "").lower()
    doi = str(entry.get("prism:doi") or "")
    return (year, title, doi)


def make_key(entry: Dict[str, Any], used_keys: set[str]) -> str:
    authors = format_authors(entry.get("dc:creator"))
    first_author = authors.split(" and ", 1)[0] if authors else "unknown"
    surname = first_author.split(",", 1)[0].strip() if "," in first_author else first_author.split()[0].strip()

    title = str(entry.get("dc:title") or "")
    title_bits = [bit for bit in re.split(r"[^A-Za-z0-9]+", title) if bit]
    title_slug = "".join(ascii_slug(bit).capitalize() for bit in title_bits[:4]) or "Record"

    base = f"{ascii_slug(surname).lower()}{get_year(entry)}{title_slug}"
    if not base:
        base = "record"

    candidate = base
    suffix = ord("a")
    while candidate in used_keys:
        candidate = f"{base}{chr(suffix)}"
        suffix += 1
    used_keys.add(candidate)
    return candidate


def format_entry(entry_type: str, key: str, fields: Dict[str, str]) -> str:
    lines = [f"@{entry_type}{{{key},"]
    for name, value in fields.items():
        lines.append(f"  {name:<8} = {{{value}}},")
    if lines[-1].endswith(","):
        lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def convert(input_path: Path, output_path: Path) -> Dict[str, Any]:
    entries = load_scopus_entries(input_path)
    entries = sorted(entries, key=entry_sort_key, reverse=True)

    used_keys: set[str] = set()
    rendered_entries: List[str] = []
    type_counts: Counter[str] = Counter()
    skipped_count = 0

    for entry in entries:
        bib_type = get_entry_type(entry)
        fields = get_entry_fields(entry, bib_type)

        if "title" not in fields:
            skipped_count += 1
            continue

        key = make_key(entry, used_keys)
        rendered_entries.append(format_entry(bib_type, key, fields))
        type_counts[bib_type] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(rendered_entries) + "\n", encoding="utf-8")

    return {
        "input_count": len(entries),
        "written_count": len(rendered_entries),
        "skipped_count": skipped_count,
        "type_counts": type_counts,
        "output_path": str(output_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a merged Scopus JSON export into a BibTeX file."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="parsifal_scopus_merged.json",
        help="Path to the merged Scopus JSON export.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="references/parsifal_scopus.bib",
        help="Path for the generated BibTeX file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = convert(Path(args.input), Path(args.output))
    counts = ", ".join(f"{name}={count}" for name, count in sorted(summary["type_counts"].items()))
    print(f"Wrote {summary['written_count']} BibTeX entries to {summary['output_path']}")
    if summary["skipped_count"]:
        print(f"Skipped {summary['skipped_count']} records without titles")
    if counts:
        print(f"Entry types: {counts}")


if __name__ == "__main__":
    main()
