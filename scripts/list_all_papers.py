
import csv

csv_path = r'd:\Master\SLR draft\data\SLR - SLR-Deep.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        idx = row.get('#', '').strip()
        title = row.get('title', '').strip()
        if not title:
            continue
        eval_col = row.get('eval', '').strip()
        er_col = str(row.get('ER', '')).strip()
        print(f"#{idx}: {title}")
        print(f"  Eval metrics: {eval_col}")
        print(f"  ER: {er_col}")
        print()
