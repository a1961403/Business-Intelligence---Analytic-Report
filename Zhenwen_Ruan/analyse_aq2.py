"""Pairwise association analysis. Run with Python 3 and numpy installed."""
import csv
import json
import math
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import numpy as np

source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / 'data' / 'ba_jobs_clean.csv'
out = Path(__file__).parent / 'evidence'
out.mkdir(exist_ok=True)
with source.open(encoding='utf-8-sig', newline='') as handle:
    jobs = list(csv.DictReader(handle))
transactions = [set(json.loads(row['skills_normalized_json'])) - {'business analysis'} for row in jobs]
n = len(jobs)
frequency = Counter(skill for skills in transactions for skill in skills)
vocabulary = sorted(skill for skill, count in frequency.items() if count >= math.ceil(n * .01))
matrix = np.array([[skill in skills for skill in vocabulary] for skills in transactions], dtype=np.int64)

def export(name, rows):
    with (out / name).open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def metrics(a, b, both, size):
    return {'n_A': int(a), 'n_B': int(b), 'n_both': int(both), 'support': float(both/size),
            'confidence': float(both/a) if a else 0., 'lift': float(both*size/(a*b)) if a*b else 0.,
            'jaccard': float(both/(a+b-both)) if a+b-both else 0.}

def rules_for(data):
    counts = data.sum(axis=0)
    overlap = data.T @ data
    rules = []
    for i, j in combinations(range(len(vocabulary)), 2):
        for a, b in [(i,j),(j,i)]:
            rules.append({'A': vocabulary[a], 'B': vocabulary[b], **metrics(counts[a], counts[b], overlap[a,b], len(data))})
    return rules

rules = rules_for(matrix)
export('all_pair_rules.csv', rules)
sensitivity = []
for support, confidence, lift in product([.01,.02,.05,.10],[.5,.6,.7],[1.0,1.2,1.5]):
    chosen = [r for r in rules if r['support'] >= support and r['confidence'] >= confidence and r['lift'] >= lift]
    sensitivity.append({'min_support':support,'min_pair_count':math.ceil(support*n),'min_confidence':confidence,'min_lift':lift,'directed_rules':len(chosen),'unique_pairs':len({tuple(sorted((r['A'],r['B']))) for r in chosen})})
export('threshold_sensitivity.csv', sensitivity)

def select(rules):
    return [r for r in rules if r['support'] >= .05 and r['confidence'] >= .6 and r['lift'] >= 1.2]

chosen = sorted(select(rules), key=lambda r:(-r['lift'],-r['support'],r['A']))
export('selected_rules.csv', chosen)
top_pairs = sorted([r for r in rules if r['A'] < r['B'] and r['support'] >= .05], key=lambda r:-r['jaccard'])
export('jaccard_pairs.csv',top_pairs)
rng = np.random.default_rng(20261114)
indices = rng.permutation(n)
train_indices = indices[:int(.7*n)]
test_indices = indices[int(.7*n):]
train_rules = select(rules_for(matrix[train_indices]))
test_lookup = {(r['A'],r['B']): r for r in rules_for(matrix[test_indices])}
validation = []
for rule in train_rules:
    test = test_lookup[(rule['A'],rule['B'])]
    validation.append({'A':rule['A'],'B':rule['B'],'train_support':rule['support'],'train_confidence':rule['confidence'],'train_lift':rule['lift'], 'test_n_both':test['n_both'],'test_support':test['support'],'test_confidence':test['confidence'],'test_lift':test['lift'],'test_lift_gt_1':int(test['lift']>1),'test_meets_thresholds':int(bool(select([test])))})
export('split_validation.csv',validation)
export('split_membership.csv',[{'job_link':jobs[i]['job_link'],'subset':'train' if i in set(train_indices) else 'test'} for i in range(n)])
summary = {'n':n,'total_skills_excluding_defining':len(frequency),'skills_occurring_once':sum(c==1 for c in frequency.values()),'skills_below_20':sum(c<20 for c in frequency.values()),'retained_skills':len(vocabulary),'tested_unique_pairs':len(vocabulary)*(len(vocabulary)-1)//2,'selected_rules':len(chosen),'selected_unique_pairs':len({tuple(sorted((r['A'],r['B']))) for r in chosen}),'train_n':len(train_indices),'test_n':len(test_indices),'train_selected_rules':len(train_rules),'test_positive_lift':sum(r['test_lift_gt_1'] for r in validation),'test_retained_rules':sum(r['test_meets_thresholds'] for r in validation),'skill_counts':dict(frequency.most_common(30))}
(out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
print('SELECTED RULES', json.dumps(chosen[:25],indent=2))
print('SENSITIVITY',json.dumps([r for r in sensitivity if r['min_confidence']==.6],indent=2))
