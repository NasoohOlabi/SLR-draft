# -*- coding: utf-8 -*-
"""
Verification script for RQ1 claims in rq1_literature_state.tex
Reads SLR-Deep sheet from SLR.xlsx and verifies all statistical claims
"""

import pandas as pd
import re
from collections import defaultdict
from difflib import SequenceMatcher
import sys

# Configure output encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def read_slr_data(excel_path):
    """Load Excel sheet and return DataFrame"""
    try:
        df = pd.read_excel(excel_path, sheet_name='SLR-Deep')
        print(f"✓ Loaded {len(df)} papers from {excel_path}")
        return df
    except Exception as e:
        print(f"✗ Error loading Excel file: {e}")
        return None


def parse_bib_file(bib_path):
    """Parse BibTeX file and return dict of citation_key -> paper_info"""
    bib_data = {}
    try:
        with open(bib_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by @ entries
        entries = re.split(r'@(\w+)\{', content)[1:]  # Skip first empty element
        
        for i in range(0, len(entries), 2):
            if i + 1 >= len(entries):
                break
            entry_type = entries[i]
            entry_content = entries[i + 1]
            
            # Extract citation key
            key_match = re.match(r'([^,]+),', entry_content)
            if not key_match:
                continue
            citation_key = key_match.group(1).strip()
            
            # Extract title
            title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ""
            
            # Extract year
            year_match = re.search(r'year\s*=\s*\{?(\d{4})\}?', entry_content, re.IGNORECASE)
            year = year_match.group(1) if year_match else ""
            
            # Extract authors (first author for matching)
            author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry_content, re.IGNORECASE)
            authors = author_match.group(1) if author_match else ""
            first_author = authors.split(',')[0].strip() if authors else ""
            
            # Extract venue/journal
            journal_match = re.search(r'journal\s*=\s*\{([^}]+)\}', entry_content, re.IGNORECASE)
            booktitle_match = re.search(r'booktitle\s*=\s*\{([^}]+)\}', entry_content, re.IGNORECASE)
            publisher_match = re.search(r'publisher\s*=\s*\{([^}]+)\}', entry_content, re.IGNORECASE)
            
            # Combine all venue information
            venue_parts = []
            if journal_match:
                venue_parts.append(journal_match.group(1))
            if booktitle_match:
                venue_parts.append(booktitle_match.group(1))
            if publisher_match:
                venue_parts.append(publisher_match.group(1))
            venue = " ".join(venue_parts)
            
            bib_data[citation_key] = {
                'title': title,
                'year': year,
                'authors': authors,
                'first_author': first_author,
                'venue': venue,
                'type': entry_type
            }
        
        print(f"✓ Parsed {len(bib_data)} entries from {bib_path}")
        return bib_data
    except Exception as e:
        print(f"✗ Error parsing BibTeX file: {e}")
        return {}


def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def match_papers_to_bib(df, bib_data):
    """Match papers from Excel to BibTeX entries"""
    matches = {}
    unmatched = []
    
    for idx, row in df.iterrows():
        title = str(row.get('title', '')).strip()
        year = str(row.get('Year', '')).strip()
        
        if not title or title == 'nan':
            continue
        
        best_match = None
        best_score = 0.0
        
        # Try to find matching BibTeX entry
        for key, bib_info in bib_data.items():
            bib_title = bib_info['title']
            bib_year = bib_info['year']
            
            # Calculate title similarity
            title_sim = similarity(title, bib_title)
            
            # Bonus for year match
            year_bonus = 0.1 if year == bib_year else 0
            
            total_score = title_sim + year_bonus
            
            if total_score > best_score:
                best_score = total_score
                best_match = key
        
        # Use threshold of 0.7 for matching
        if best_match and best_score >= 0.7:
            matches[idx] = {
                'citation_key': best_match,
                'title': title,
                'year': year,
                'match_score': best_score,
                'bib_info': bib_data[best_match]
            }
        else:
            unmatched.append({
                'title': title,
                'year': year,
                'best_match': best_match if best_match else None,
                'best_score': best_score
            })
    
    print(f"✓ Matched {len(matches)}/{len(df)} papers to BibTeX entries")
    if unmatched:
        print(f"  ⚠ {len(unmatched)} papers could not be matched")
    
    return matches, unmatched


def classify_model_type(llm_text):
    """Categorize LLM string into open-weight/proprietary/custom"""
    if pd.isna(llm_text) or not str(llm_text).strip():
        return 'unknown'
    
    llm_lower = str(llm_text).lower()
    
    # Custom/from-scratch indicators (check first, as it's most specific)
    custom_keywords = [
        'trained from scratch', 'from scratch', 'custom architecture',
        'vae', 'autoencoder', 'encoder-decoder'
    ]
    
    # Check for custom/from-scratch first (most specific)
    for keyword in custom_keywords:
        if keyword in llm_lower:
            return 'custom'
    
    # Proprietary models (check before open-weight as more specific)
    proprietary_keywords = [
        'gpt-3.5', 'gpt3.5', 'gpt-4', 'gpt4', 'gpt-3', 'gpt3',
        'chatgpt', 'chat gpt', 'openai', 'babbage', 'davinci'
    ]
    
    for keyword in proprietary_keywords:
        if keyword in llm_lower:
            return 'proprietary'
    
    # Open-weight models
    open_weight_keywords = [
        'gpt-2', 'gpt2', 'llama', 'llama2', 'llama-2',
        'bert', 'opt', 'bart', 'roberta', 'distilbert',
        't5', 'albert', 'electra', 'baichuan', 'ctrl'
    ]
    
    # Check for open-weight
    for keyword in open_weight_keywords:
        if keyword in llm_lower:
            return 'open-weight'
    
    # If contains LSTM/RNN but also mentions BERT/GPT-2, it's likely open-weight
    if any(term in llm_lower for term in ['lstm', 'rnn']) and \
       any(term in llm_lower for term in ['bert', 'gpt', 'transformer']):
        return 'open-weight'
    
    # If only LSTM/RNN without open-weight models, it's custom
    if any(term in llm_lower for term in ['lstm', 'rnn']) and \
       not any(term in llm_lower for term in open_weight_keywords):
        return 'custom'
    
    # Default to unknown if we can't classify
    return 'unknown'


def verify_publication_trends(df, matches):
    """Count papers by year period"""
    trends = {
        '2020': [],
        '2021-2022': [],
        '2023': [],
        '2024-2025': []
    }
    
    for idx, row in df.iterrows():
        year_str = str(row.get('Year', '')).strip()
        if not year_str or year_str == 'nan':
            continue
        
        try:
            year = int(float(year_str))
            title = str(row.get('title', '')).strip()
            citation_key = matches.get(idx, {}).get('citation_key', 'N/A')
            
            paper_info = {
                'title': title,
                'year': year,
                'citation': citation_key
            }
            
            if year == 2020:
                trends['2020'].append(paper_info)
            elif 2021 <= year <= 2022:
                trends['2021-2022'].append(paper_info)
            elif year == 2023:
                trends['2023'].append(paper_info)
            elif 2024 <= year <= 2025:
                trends['2024-2025'].append(paper_info)
        except (ValueError, TypeError):
            continue
    
    return trends


def verify_model_usage(df, matches):
    """Calculate percentages for model types"""
    model_counts = defaultdict(list)
    
    for idx, row in df.iterrows():
        llm_text = row.get('LLM', '')
        model_type = classify_model_type(llm_text)
        title = str(row.get('title', '')).strip()
        citation_key = matches.get(idx, {}).get('citation_key', 'N/A')
        
        paper_info = {
            'title': title,
            'llm': str(llm_text),
            'citation': citation_key
        }
        
        model_counts[model_type].append(paper_info)
    
    total = len([p for p in model_counts.values() for _ in p])
    if total == 0:
        return model_counts, {}
    
    percentages = {
        'open-weight': (len(model_counts['open-weight']) / total * 100) if total > 0 else 0,
        'proprietary': (len(model_counts['proprietary']) / total * 100) if total > 0 else 0,
        'custom': (len(model_counts['custom']) / total * 100) if total > 0 else 0,
        'unknown': (len(model_counts['unknown']) / total * 100) if total > 0 else 0
    }
    
    return model_counts, percentages


def verify_publication_venues(df, matches, bib_data):
    """Categorize papers by venue type"""
    venues = {
        'arxiv': [],
        'top-tier': [],
        'specialized': []
    }
    
    top_tier_keywords = [
        'acl', 'neurips', 'iclr', 'icml', 'aaai', 'ijcai',
        'sigir', 'emnlp', 'naacl', 'eacl', 'coling',
        'ieee symposium on security', 'sp ', 'ccs', 'usenix',
        'acm sigsac', 'computer and communications security',
        'international conference on multimedia', 'mm ', 'acm mm'
    ]
    
    for idx, row in df.iterrows():
        title = str(row.get('title', '')).strip()
        citation_key = matches.get(idx, {}).get('citation_key', 'N/A')
        bib_info = matches.get(idx, {}).get('bib_info', {})
        venue = bib_info.get('venue', '').lower()
        entry_type = bib_info.get('type', '').lower()
        
        paper_info = {
            'title': title,
            'venue': venue,
            'citation': citation_key,
            'type': entry_type
        }
        
        # Check if it's an arXiv preprint
        if 'arxiv' in venue or entry_type == 'article' and 'preprint' in venue:
            venues['arxiv'].append(paper_info)
        # Check for top-tier venues
        elif any(keyword in venue for keyword in top_tier_keywords):
            venues['top-tier'].append(paper_info)
        # Everything else is specialized
        else:
            venues['specialized'].append(paper_info)
    
    total = sum(len(v) for v in venues.values())
    if total == 0:
        return venues, {}
    
    percentages = {
        'arxiv': len(venues['arxiv']) / total * 100,
        'top-tier': len(venues['top-tier']) / total * 100,
        'specialized': len(venues['specialized']) / total * 100
    }
    
    return venues, percentages


def generate_report(df, matches, bib_data, output_path):
    """Generate markdown report with all findings"""
    
    # Verify all claims
    trends = verify_publication_trends(df, matches)
    model_counts, model_percentages = verify_model_usage(df, matches)
    venues, venue_percentages = verify_publication_venues(df, matches, bib_data)
    
    report = []
    report.append("# RQ1 Claims Verification Report\n")
    report.append("This report verifies all statistical claims in `sections/rq1_literature_state.tex`\n")
    report.append(f"**Total papers analyzed:** {len(df)}\n")
    report.append(f"**Papers matched to BibTeX:** {len(matches)}\n\n")
    
    # Publication Trends
    report.append("## 1. Publication Trends by Year\n")
    report.append("| Period | Claimed | Actual | Papers |\n")
    report.append("|--------|---------|--------|--------|\n")
    
    claimed_trends = {'2020': 2, '2021-2022': 3, '2023': 4, '2024-2025': 17, 'Total': 26}
    actual_totals = {k: len(v) for k, v in trends.items()}
    actual_total = sum(actual_totals.values())
    
    for period in ['2020', '2021-2022', '2023', '2024-2025']:
        claimed = claimed_trends.get(period, 0)
        actual = actual_totals.get(period, 0)
        status = "✓" if claimed == actual else "✗"
        report.append(f"| {period} | {claimed} | {actual} {status} | {len(trends[period])} |\n")
    
    report.append(f"| **Total** | {claimed_trends['Total']} | {actual_total} {'✓' if claimed_trends['Total'] == actual_total else '✗'} | {actual_total} |\n\n")
    
    # Detailed paper lists by year
    report.append("### Papers by Year Period\n")
    for period, papers in trends.items():
        if papers:
            report.append(f"#### {period} ({len(papers)} papers)\n")
            for paper in papers:
                citation = f"\\cite{{{paper['citation']}}}" if paper['citation'] != 'N/A' else "(No citation)"
                report.append(f"- {paper['title']} ({paper['year']}) {citation}\n")
            report.append("\n")
    
    # Model Usage
    report.append("## 2. Model Usage Distribution\n")
    report.append("| Model Type | Claimed % | Actual % | Count | Papers |\n")
    report.append("|------------|-----------|----------|-------|--------|\n")
    
    claimed_models = {'open-weight': 80, 'proprietary': 12, 'custom': 8}
    for model_type in ['open-weight', 'proprietary', 'custom']:
        claimed = claimed_models.get(model_type, 0)
        actual = model_percentages.get(model_type, 0)
        count = len(model_counts.get(model_type, []))
        status = "✓" if abs(claimed - actual) < 5 else "✗"  # Allow 5% tolerance
        report.append(f"| {model_type.replace('-', ' ').title()} | {claimed}% | {actual:.1f}% {status} | {count} | {count} |\n")
    
    report.append("\n### Open-Weight Models (Papers) - Complete List with Citations\n")
    report.append("**Total: {} papers using open-weight models**\n\n".format(len(model_counts.get('open-weight', []))))
    for i, paper in enumerate(model_counts.get('open-weight', []), 1):
        citation = f"\\cite{{{paper['citation']}}}" if paper['citation'] != 'N/A' else "(No citation)"
        report.append(f"{i}. {paper['title']} {citation}\n")
        # Show full LLM description if available
        llm_desc = paper['llm'].replace('\n', ' ').strip()
        if len(llm_desc) > 150:
            llm_desc = llm_desc[:147] + "..."
        report.append(f"   - **LLM Used:** {llm_desc}\n")
    
    report.append("\n### Proprietary Models (Papers)\n")
    for paper in model_counts.get('proprietary', []):
        citation = f"\\cite{{{paper['citation']}}}" if paper['citation'] != 'N/A' else "(No citation)"
        report.append(f"- {paper['title']} {citation}\n")
        report.append(f"  - LLM: {paper['llm'][:100]}...\n")
    
    report.append("\n### Custom/From-Scratch Models (Papers)\n")
    for paper in model_counts.get('custom', []):
        citation = f"\\cite{{{paper['citation']}}}" if paper['citation'] != 'N/A' else "(No citation)"
        report.append(f"- {paper['title']} {citation}\n")
        report.append(f"  - LLM: {paper['llm'][:100]}...\n")
    
    # Publication Venues
    report.append("\n## 3. Publication Venues\n")
    report.append("| Venue Type | Claimed % | Actual % | Count |\n")
    report.append("|------------|-----------|----------|-------|\n")
    
    claimed_venues = {'arxiv': 60, 'top-tier': 25, 'specialized': 15}
    for venue_type in ['arxiv', 'top-tier', 'specialized']:
        claimed = claimed_venues.get(venue_type, 0)
        actual = venue_percentages.get(venue_type, 0)
        count = len(venues.get(venue_type, []))
        status = "✓" if abs(claimed - actual) < 5 else "✗"
        report.append(f"| {venue_type.replace('-', ' ').title()} | {claimed}% | {actual:.1f}% {status} | {count} |\n")
    
    report.append("\n### Papers by Venue Type\n")
    for venue_type, papers in venues.items():
        if papers:
            report.append(f"#### {venue_type.replace('-', ' ').title()} ({len(papers)} papers)\n")
            for paper in papers[:10]:  # Show first 10
                citation = f"\\cite{{{paper['citation']}}}" if paper['citation'] != 'N/A' else "(No citation)"
                report.append(f"- {paper['title']} {citation}\n")
            if len(papers) > 10:
                report.append(f"... and {len(papers) - 10} more\n")
            report.append("\n")
    
    # Summary
    report.append("\n## Summary\n")
    report.append("### Key Findings\n")
    report.append(f"- Total papers in dataset: {len(df)}\n")
    report.append(f"- Papers matched to BibTeX: {len(matches)}\n")
    report.append(f"- Publication trends: {actual_total} papers total (claimed: {claimed_trends['Total']})\n")
    report.append(f"- Model usage: {len(model_counts['open-weight'])} open-weight ({model_percentages.get('open-weight', 0):.1f}%), {len(model_counts['proprietary'])} proprietary ({model_percentages.get('proprietary', 0):.1f}%), {len(model_counts['custom'])} custom ({model_percentages.get('custom', 0):.1f}%)\n")
    report.append(f"- Venue distribution: {len(venues['arxiv'])} arXiv ({venue_percentages.get('arxiv', 0):.1f}%), {len(venues['top-tier'])} top-tier ({venue_percentages.get('top-tier', 0):.1f}%), {len(venues['specialized'])} specialized ({venue_percentages.get('specialized', 0):.1f}%)\n")
    
    # Discrepancies
    report.append("\n### Discrepancies with Claims\n")
    discrepancies = []
    
    if abs(claimed_trends['Total'] - actual_total) > 0:
        discrepancies.append(f"- Publication total: claimed {claimed_trends['Total']}, actual {actual_total}")
    
    if abs(claimed_models['open-weight'] - model_percentages.get('open-weight', 0)) > 5:
        discrepancies.append(f"- Open-weight models: claimed {claimed_models['open-weight']}%, actual {model_percentages.get('open-weight', 0):.1f}%")
    
    if abs(claimed_venues['arxiv'] - venue_percentages.get('arxiv', 0)) > 5:
        discrepancies.append(f"- arXiv venues: claimed {claimed_venues['arxiv']}%, actual {venue_percentages.get('arxiv', 0):.1f}%")
    
    if discrepancies:
        for disc in discrepancies:
            report.append(f"{disc}\n")
    else:
        report.append("- No significant discrepancies found.\n")
    
    # Citation list for LaTeX
    report.append("\n### Citation List for Open-Weight Models (for LaTeX)\n")
    open_weight_citations = [p['citation'] for p in model_counts.get('open-weight', []) if p['citation'] != 'N/A']
    if open_weight_citations:
        report.append("```latex\n")
        report.append(", ".join(open_weight_citations))
        report.append("\n```\n")
        report.append("\nOr in LaTeX format:\n")
        report.append("```latex\n")
        report.append("\\cite{" + "}\n\\cite{".join(open_weight_citations) + "}\n")
        report.append("```\n")
    
    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    print(f"✓ Generated verification report: {output_path}")
    return report


if __name__ == "__main__":
    excel_path = "./SLR.xlsx"
    bib_path = "./references/SLR.bib"
    output_path = "./rq1_verification_report.md"
    
    print("=" * 60)
    print("RQ1 Claims Verification")
    print("=" * 60)
    
    # Read data
    df = read_slr_data(excel_path)
    if df is None:
        sys.exit(1)
    
    # Parse BibTeX
    bib_data = parse_bib_file(bib_path)
    if not bib_data:
        sys.exit(1)
    
    # Match papers to BibTeX
    matches, unmatched = match_papers_to_bib(df, bib_data)
    
    # Generate report
    generate_report(df, matches, bib_data, output_path)
    
    print("\n" + "=" * 60)
    print("Verification complete!")
    print("=" * 60)

