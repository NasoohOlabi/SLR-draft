
import csv
import re

csv_path = r'd:\Master\SLR draft\data\SLR - SLR-Deep.csv'

papers_with_capacity = []
keywords = ['BPW', 'BPT', 'Bits Per Word', 'Bits Per Token', 'ER', 'Embedding Rate', 'Capacity', 'bps', 'bits/word', 'bits/token']

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row.get('title', '').strip()
        if not title:
            continue
        eval_col = row.get('eval', '').strip()
        er_col = str(row.get('ER', '')).strip()
        combined_text = (eval_col + ' ' + er_col).lower()
        
        found = False
        for kw in keywords:
            if kw.lower() in combined_text:
                found = True
                break
        if found:
            papers_with_capacity.append(title)

print(f"Total papers with capacity/ER metrics: {len(papers_with_capacity)}")
print("\nPapers:")
for i, title in enumerate(papers_with_capacity, 1):
    print(f"{i}. {title}")
