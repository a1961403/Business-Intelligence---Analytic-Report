import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

jobs = pd.read_csv('ba_jobs_clean.csv')
skills_long = pd.read_csv('ba_skills_long.csv')

top10_emp = jobs['company'].value_counts().head(10).index.tolist()
jobs_top10 = jobs[jobs['company'].isin(top10_emp)].copy()

skill_counts = skills_long[skills_long['skill'] != 'business analysis'][
    'skill'
].value_counts()
top10_skills = skill_counts.head(10).index.tolist()

matrix_pct = pd.DataFrame(index=top10_emp, columns=top10_skills, dtype=float)

for emp in top10_emp:
  emp_links = set(jobs_top10[jobs_top10['company'] == emp]['job_link'])
  n_emp = len(emp_links)
  for sk in top10_skills:
    sk_links = set(skills_long[skills_long['skill'] == sk]['job_link'])
    cnt = len(emp_links.intersection(sk_links))
    matrix_pct.loc[emp, sk] = (cnt / n_emp) * 100

short_emp_names = [e if len(e) <= 28 else e[:25] + '...' for e in top10_emp]
plot_df = matrix_pct.copy()
plot_df.index = [
    f"{name} (n={jobs_top10[jobs_top10['company']==orig].shape[0]})"
    for name, orig in zip(short_emp_names, top10_emp)
]
plot_df.columns = [c.title() if c != 'sql' else 'SQL' for c in top10_skills]

plt.figure(figsize=(11, 6))
sns.heatmap(
    plot_df,
    annot=True,
    fmt='.1f',
    cmap='YlGnBu',
    cbar_kws={'label': 'Skill Prevalence (%)'},
    linewidths=0.5,
)

plt.title(
    'Figure 1: Prevalence of Top 10 Associated Skills Across Leading Observed'
    ' Employers (%)',
    fontsize=12,
    fontweight='bold',
    pad=12,
)
plt.xlabel('Associated Skill', fontsize=10, fontweight='bold')
plt.ylabel('Leading Observed Employer', fontsize=10, fontweight='bold')
plt.xticks(rotation=30, ha='right')

plt.tight_layout()
plt.savefig('Figure_4_1_Employer_Skill_Heatmap.png', dpi=300)
plt.show()