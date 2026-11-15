from pathlib import Path
import csv,json
root=Path(__file__).parent
with (root/'data/ba_jobs_clean.csv').open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
with (root/'evidence/profile_membership.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['job_link','tableau_sql','process_improvement_project_management']);w.writeheader()
 for row in rows:
  s=set(json.loads(row['skills_normalized_json']))
  w.writerow({'job_link':row['job_link'],'tableau_sql':int({'tableau','sql'}<=s),'process_improvement_project_management':int({'process improvement','project management'}<=s)})
