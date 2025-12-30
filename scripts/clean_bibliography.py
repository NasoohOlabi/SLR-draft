#!/usr/bin/env python3
"""
BibTeX Duplicate Cleaner Script

This script processes a BibTeX bibliography file to:
1. Remove identical entries (same key and same content)
2. Report entries with the same key but different data
3. Write the cleaned file back
4. Print a summary report to console
"""

import re
import sys
from collections import defaultdict
from typing import List, Dict, Tuple, Set


class BibEntry:
    """Represents a BibTeX entry with its key, type, and content."""
    
    def __init__(self, key: str, entry_type: str, content: str, original_lines: Tuple[int, int]):
        self.key = key
        self.entry_type = entry_type
        self.content = content
        self.original_lines = original_lines  # (start_line, end_line) for reference
    
    def __repr__(self):
        return f"BibEntry(key='{self.key}', type='{self.entry_type}', lines={self.original_lines})"


def parse_bibtex(file_path: str) -> List[BibEntry]:
    """
    Parse BibTeX entries from a .bib file.
    Uses brace matching to handle nested braces correctly.
    
    Returns a list of BibEntry objects.
    """
    entries = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    i = 0
    content_len = len(content)
    
    while i < content_len:
        # Find next @ symbol
        if content[i] != '@':
            i += 1
            continue
        
        # Mark start of entry
        entry_start = i
        start_line = content[:entry_start].count('\n') + 1
        
        # Skip @
        i += 1
        
        # Extract entry type (skip whitespace first)
        while i < content_len and content[i].isspace():
            i += 1
        
        entry_type_start = i
        while i < content_len and (content[i].isalnum() or content[i] == '_'):
            i += 1
        entry_type = content[entry_type_start:i]
        
        if not entry_type:
            i += 1
            continue
        
        # Skip whitespace before opening brace
        while i < content_len and content[i].isspace():
            i += 1
        
        if i >= content_len or content[i] != '{':
            i += 1
            continue
        
        # Find matching closing brace for the entire entry
        brace_start = i
        brace_count = 1
        i += 1  # Skip opening brace
        
        # Extract key (everything until first comma at brace level 1)
        key_start = i
        key_end = -1
        
        while i < content_len and brace_count > 0:
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Entry ends, key is everything before this
                    key_end = i
                    break
            elif brace_count == 1 and content[i] == ',':
                # Found comma at top level - this ends the key
                key_end = i
                break
            i += 1
        
        if key_end == -1:
            # Malformed entry
            i += 1
            continue
        
        # Extract key
        key = content[key_start:key_end].strip()
        
        if not key:
            # No key found, skip
            i += 1
            continue
        
        # Find the end of the entry (matching closing brace)
        # Reset to brace start
        i = brace_start
        brace_count = 1
        i += 1  # Skip opening brace
        
        entry_end = -1
        while i < content_len:
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    entry_end = i + 1  # Include closing brace
                    break
            i += 1
        
        if entry_end == -1:
            # Malformed entry
            i += 1
            continue
        
        # Successfully found complete entry
        end_line = content[:entry_end].count('\n') + 1
        full_entry = content[entry_start:entry_end]
        
        entries.append(BibEntry(key, entry_type, full_entry, (start_line, end_line)))
        
        # Move to after this entry
        i = entry_end
    
    return entries


def normalize_content(content: str) -> str:
    """
    Normalize BibTeX entry content for comparison.
    - Remove extra whitespace
    - Normalize line breaks
    - Case-insensitive field comparison
    """
    # Remove all whitespace (spaces, tabs, newlines) for comparison
    normalized = re.sub(r'\s+', '', content)
    # Convert to lowercase for case-insensitive comparison
    normalized = normalized.lower()
    return normalized


def find_duplicates(entries: List[BibEntry]) -> Dict[str, List[int]]:
    """
    Find identical entries (same normalized content).
    
    Returns a dictionary mapping normalized content to list of entry indices.
    """
    content_map = defaultdict(list)
    
    for idx, entry in enumerate(entries):
        normalized = normalize_content(entry.content)
        content_map[normalized].append(idx)
    
    # Return only entries that appear more than once
    duplicates = {content: indices for content, indices in content_map.items() if len(indices) > 1}
    return duplicates


def find_conflicts(entries: List[BibEntry]) -> Dict[str, List[int]]:
    """
    Find entries with the same key but different content.
    
    Returns a dictionary mapping keys to list of entry indices with that key.
    """
    key_map = defaultdict(list)
    
    for idx, entry in enumerate(entries):
        key_map[entry.key].append(idx)
    
    # Return only keys that appear more than once
    conflicts = {key: indices for key, indices in key_map.items() if len(indices) > 1}
    
    # Filter to only include cases where content actually differs
    actual_conflicts = {}
    for key, indices in conflicts.items():
        # Check if all entries with this key have the same content
        contents = [normalize_content(entries[i].content) for i in indices]
        if len(set(contents)) > 1:  # Different content
            actual_conflicts[key] = indices
    
    return actual_conflicts


def remove_duplicates(entries: List[BibEntry], duplicates: Dict[str, List[int]]) -> List[BibEntry]:
    """
    Remove duplicate entries, keeping only the first occurrence.
    
    Returns a list of unique entries.
    """
    # Collect indices to remove (all but first occurrence of each duplicate)
    indices_to_remove = set()
    
    for content, indices in duplicates.items():
        # Keep first, remove rest
        for idx in indices[1:]:
            indices_to_remove.add(idx)
    
    # Create new list without duplicates
    unique_entries = [entry for idx, entry in enumerate(entries) if idx not in indices_to_remove]
    
    return unique_entries


def write_cleaned_bib(entries: List[BibEntry], file_path: str):
    """
    Write cleaned entries back to the .bib file.
    Preserves original formatting as much as possible.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        for i, entry in enumerate(entries):
            f.write(entry.content)
            # Add blank line between entries (except after last)
            if i < len(entries) - 1:
                f.write('\n\n')


def generate_report(entries: List[BibEntry], duplicates: Dict[str, List[int]], 
                   conflicts: Dict[str, List[int]], removed_count: int):
    """
    Generate and print a console report with statistics and details.
    """
    print("=" * 70)
    print("BibTeX Duplicate Cleaner Report")
    print("=" * 70)
    print()
    
    print(f"Total entries processed: {len(entries) + removed_count}")
    print(f"Duplicate entries removed: {removed_count}")
    print(f"Unique entries remaining: {len(entries)}")
    print()
    
    if duplicates:
        print(f"Duplicate groups found: {len(duplicates)}")
        print("\nDuplicate entries (same key and content):")
        print("-" * 70)
        for content, indices in duplicates.items():
            # Show first entry as example
            first_idx = indices[0]
            entry = entries[first_idx] if first_idx < len(entries) else None
            if entry:
                print(f"  Key: {entry.key} ({len(indices)} occurrences)")
                print(f"    Type: {entry.entry_type}")
                print(f"    Lines: {entry.original_lines[0]}-{entry.original_lines[1]}")
            else:
                # Entry was removed, get from original list
                print(f"  {len(indices)} identical entries (all but first removed)")
        print()
    
    if conflicts:
        print(f"Conflicting keys found: {len(conflicts)}")
        print("\nEntries with same key but different data (KEPT - requires manual review):")
        print("-" * 70)
        for key, indices in conflicts.items():
            print(f"  Key: {key} ({len(indices)} occurrences with different content)")
            for idx in indices:
                entry = entries[idx]
                print(f"    - Occurrence {idx + 1}: {entry.entry_type}, lines {entry.original_lines[0]}-{entry.original_lines[1]}")
            print()
    else:
        print("No conflicting keys found (all entries with same key have identical content).")
        print()
    
    print("=" * 70)
    print("Cleaning complete!")
    print("=" * 70)


def main():
    """Main function that orchestrates the entire process."""
    bib_file = "references/bibliography.bib"
    
    print(f"Reading BibTeX file: {bib_file}")
    print()
    
    # Parse entries
    entries = parse_bibtex(bib_file)
    
    if not entries:
        print("Error: No BibTeX entries found in the file.")
        sys.exit(1)
    
    print(f"Found {len(entries)} entries.")
    print()
    
    # Find duplicates and conflicts
    duplicates = find_duplicates(entries)
    conflicts = find_conflicts(entries)
    
    # Remove duplicates (keep first occurrence)
    unique_entries = remove_duplicates(entries, duplicates)
    removed_count = len(entries) - len(unique_entries)
    
    # Write cleaned file
    if removed_count > 0:
        print(f"Writing cleaned file (removed {removed_count} duplicate entries)...")
        write_cleaned_bib(unique_entries, bib_file)
        print("File updated successfully.")
        print()
    else:
        print("No duplicates found. File unchanged.")
        print()
    
    # Generate report
    generate_report(unique_entries, duplicates, conflicts, removed_count)


if __name__ == "__main__":
    main()

