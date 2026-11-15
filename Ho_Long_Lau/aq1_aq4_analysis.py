import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

# ==========================================
# 1. Load Shared Cleaned Datasets
# ==========================================
jobs = pd.read_csv('ba_jobs_clean.csv')
skills_long = pd.read_csv('ba_skills_long.csv')

print(f"Loaded ba_jobs_clean.csv: {len(jobs)} postings")
print(f"Loaded ba_skills_long.csv: {len(skills_long)} unique posting-skill pairs")

# Exclude cohort-defining skill 'business analysis' for associated skill rankings
assoc_skills = skills_long[skills_long['skill'] != 'business analysis'].copy()
skill_counts = assoc_skills['skill'].value_counts()

top10_skills = skill_counts.head(10).index.tolist()
top15_skills = skill_counts.head(15).index.tolist()

# ==========================================
# 2. AQ1: Employer Skill Variance (Top 10 Observed Employers)
# ==========================================
top10_employers = jobs['company'].value_counts().head(10).index.tolist()
jobs_top10 = jobs[jobs['company'].isin(top10_employers)].copy()

aq1_rows = []
heatmap_data = pd.DataFrame(index=top10_employers, columns=top10_skills, dtype=float)

for sk in top10_skills:
    jobs_with_sk = set(assoc_skills[assoc_skills['skill'] == sk]['job_link'])
    jobs_top10['status'] = np.where(jobs_top10['job_link'].isin(jobs_with_sk), 'Present', 'Absent')
    
    # Construct 10 x 2 contingency table (Employer x Present/Absent)
    ct = pd.crosstab(jobs_top10['company'], jobs_top10['status']).reindex(top10_employers)
    for col in ['Present', 'Absent']:
        if col not in ct.columns:
            ct[col] = 0
    ct = ct[['Present', 'Absent']]
    
    # Calculate prevalence (%) per employer for heatmap
    heatmap_data[sk] = (ct['Present'] / (ct['Present'] + ct['Absent'])) * 100
    
    # Chi-square test of independence
    chi2, p, dof, ex = chi2_contingency(ct)
    pct_cells_below_5 = (ex < 5).sum() / ex.size * 100
    
    if p < 0.05:
        decision = "Reject H0 (Significant*)" if pct_cells_below_5 > 20 else "Reject H0 (Significant)"
    else:
        decision = "Fail to Reject H0 (Not Significant)"
        
    aq1_rows.append({
        'Associated Skill': sk.title() if sk != 'sql' else 'SQL',
        'Chi-Square (x2)': round(chi2, 2),
        'df': dof,
        'p-value': '< 0.0001' if p < 0.0001 else f"{p:.4f}",
        'Cells Expected < 5 (%)': f"{pct_cells_below_5:.1f}%",
        'Statistical Decision (alpha = 0.05)': decision
    })

aq1_table = pd.DataFrame(aq1_rows).sort_values(by='Chi-Square (x2)', ascending=False)
aq1_table.to_csv('Table_1_AQ1_ChiSquare_Results.csv', index=False)
print("\n--- Table 1: AQ1 Chi-Square Test Results ---")
print(aq1_table.to_string(index=False))

# Plot Figure 1: Heatmap of Top 10 Employers x Top 10 Associated Skills
emp_counts = jobs['company'].value_counts().loc[top10_employers]
y_labels = [f"{emp[:28] + '...' if len(emp) > 30 else emp} (n={emp_counts[emp]})" for emp in top10_employers]
x_labels = [sk.title() if sk != 'sql' else 'SQL' for sk in top10_skills]

fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
im = ax.imshow(heatmap_data.values, cmap='YlGnBu', aspect='auto', vmin=0, vmax=100)

ax.set_xticks(np.arange(len(x_labels)))
ax.set_yticks(np.arange(len(y_labels)))
ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=9.5)
ax.set_yticklabels(y_labels, fontsize=9.5)

# Annotate cells
for i in range(len(y_labels)):
    for j in range(len(x_labels)):
        val = heatmap_data.values[i, j]
        text_color = 'white' if val > 55 else 'black'
        ax.text(j, i, f"{val:.1f}", ha='center', va='center', color=text_color, fontsize=8.5)

cbar = fig.colorbar(im, ax=ax, pad=0.02)
cbar.set_label('Skill Prevalence (%)', fontsize=10)
ax.set_title('Figure 1: Prevalence of Top 10 Associated Skills Across Leading Observed Employers (%)', fontsize=11.5, fontweight='bold', pad=12)
ax.set_xlabel('Associated Skill', fontsize=10, fontweight='bold')
ax.set_ylabel('Leading Observed Employer', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('Figure_4_1_Employer_Skill_Heatmap.png', dpi=300)
plt.close()

# ==========================================
# 3. AQ4: Generic vs. Specialized/Hybrid BA Title Skill Distributions
# ==========================================
def classify_title(title):
    t_clean = str(title).strip().lower()
    # Generic BA: only standard seniority/level modifiers around 'business analyst'
    pattern = r'^(senior|sr\.?|junior|jr\.?|lead|principal|associate|staff|entry[- ]level|mid[- ]level|level\s+[i1234v]+)?\s*business analyst(\s*[-–/i1234v]+)?$'
    return 'Generic BA' if re.match(pattern, t_clean) else 'Specialized / Hybrid BA'

jobs['title_group'] = jobs['job_title'].apply(classify_title)
n_gen = (jobs['title_group'] == 'Generic BA').sum()
n_spec = (jobs['title_group'] == 'Specialized / Hybrid BA').sum()
print(f"\nTitle Classification: Generic BA = {n_gen} ({n_gen/len(jobs)*100:.2f}%), Specialized/Hybrid BA = {n_spec} ({n_spec/len(jobs)*100:.2f}%)")

aq4_rows = []
for sk in top15_skills:
    jobs_with_sk = set(assoc_skills[assoc_skills['skill'] == sk]['job_link'])
    jobs['status'] = np.where(jobs['job_link'].isin(jobs_with_sk), 'Present', 'Absent')
    
    # Construct 2 x 2 contingency table (Title Group x Present/Absent)
    ct = pd.crosstab(jobs['title_group'], jobs['status'])[['Present', 'Absent']]
    chi2, p, dof, ex = chi2_contingency(ct, correction=False)
    
    gen_cnt = ct.loc['Generic BA', 'Present']
    gen_pct = gen_cnt / n_gen * 100
    spec_cnt = ct.loc['Specialized / Hybrid BA', 'Present']
    spec_pct = spec_cnt / n_spec * 100
    diff = spec_pct - gen_pct
    
    if p < 0.05:
        decision = "Reject H0 (Higher in Specialized)" if diff > 0 else "Reject H0 (Higher in Generic)"
    else:
        decision = "Fail to Reject H0 (Not Significant)"
        
    aq4_rows.append({
        'Associated Skill': sk.title() if sk != 'sql' else 'SQL',
        'Generic BA (n=731)': f"{gen_cnt} ({gen_pct:.2f}%)",
        'Specialized BA (n=1198)': f"{spec_cnt} ({spec_pct:.2f}%)",
        'Diff (Spec - Gen)': f"{diff:+.2f}%",
        'Chi-Square (x2)': round(chi2, 2),
        'p-value': f"{p:.4f}",
        'Statistical Decision (alpha = 0.05)': decision,
        '_gen_pct': gen_pct,
        '_spec_pct': spec_pct,
        '_p_raw': p
    })

aq4_df = pd.DataFrame(aq4_rows)
aq4_export = aq4_df.drop(columns=['_gen_pct', '_spec_pct', '_p_raw'])
aq4_export.to_csv('Table_2_AQ4_Title_ChiSquare_Results.csv', index=False)
print("\n--- Table 2: AQ4 Title Group Chi-Square Test Results ---")
print(aq4_export.to_string(index=False))

# Plot Figure 2: Grouped Horizontal Bar Chart for AQ4
plot_df = aq4_df.iloc[::-1].reset_index(drop=True)
labels = []
for _, r in plot_df.iterrows():
    p_val = r['_p_raw']
    stars = ' ***' if p_val < 0.001 else (' **' if p_val < 0.01 else (' *' if p_val < 0.05 else ''))
    labels.append(r['Associated Skill'] + stars)

y = np.arange(len(labels))
height = 0.38

fig, ax = plt.subplots(figsize=(10.5, 7.2), dpi=300)
rects1 = ax.barh(y + height/2, plot_df['_gen_pct'], height, label=f'Generic BA (n = {n_gen})', color='#5B84B1')
rects2 = ax.barh(y - height/2, plot_df['_spec_pct'], height, label=f'Specialized / Hybrid BA (n = {n_spec})', color='#002147')

for rect in rects1:
    w = rect.get_width()
    ax.text(w + 0.6, rect.get_y() + rect.get_height()/2, f'{w:.1f}%', va='center', ha='left', fontsize=8, color='#374151')

for rect in rects2:
    w = rect.get_width()
    ax.text(w + 0.6, rect.get_y() + rect.get_height()/2, f'{w:.1f}%', va='center', ha='left', fontsize=8, color='#002147', fontweight='bold')

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=9.5)
ax.set_xlabel('Prevalence in Job Postings (%)', fontsize=10, fontweight='bold')
ax.set_title('Figure 2: Top 15 Associated Skills Prevalence — Generic vs. Specialized/Hybrid BA (%)', fontsize=11.5, fontweight='bold', pad=12)
ax.set_xlim(0, 63)
ax.grid(axis='x', linestyle='--', alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(loc='lower right', frameon=True, fontsize=9.5)

plt.figtext(0.01, 0.01, 'Note: Asterisks indicate statistically significant differences via Chi-square test (* p < 0.05, ** p < 0.01, *** p < 0.001).', fontsize=8.5, style='italic', color='#4B5563')
plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('Figure_4_4_Title_Skill_Comparison.png', dpi=300)
plt.close()

print("\nAll tables (CSV) and figures (PNG) generated successfully!")