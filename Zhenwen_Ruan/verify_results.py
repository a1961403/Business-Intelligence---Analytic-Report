from pathlib import Path
import csv,json,hashlib
root=Path(__file__).parent
s=json.loads((root/'evidence/summary.json').read_text())
for k,v in {'n':1929,'retained_skills':266,'tested_unique_pairs':35245,'selected_rules':24,'train_n':1350,'test_n':579,'train_selected_rules':26,'test_positive_lift':25,'test_retained_rules':18}.items():
 assert s[k]==v,(k,s[k],v)
with (root/'evidence/profile_membership.csv').open(encoding='utf-8-sig') as f: r=list(csv.DictReader(f))
a=[int(x['tableau_sql']) for x in r]; b=[int(x['process_improvement_project_management']) for x in r]
assert (sum(a),sum(b),sum(x*y for x,y in zip(a,b)))==(112,119,7)
expected=json.loads((root/'expected_numeric_sha256.json').read_text())
for name,digest in expected.items():
 assert hashlib.sha256((root/'evidence'/name).read_bytes()).hexdigest()==digest, name+' differs from original report evidence'
print('PASS: headline counts, profiles and every original numerical evidence file match.')
