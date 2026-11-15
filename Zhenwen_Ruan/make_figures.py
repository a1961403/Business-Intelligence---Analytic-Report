from pathlib import Path
import csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
root = Path(__file__).parent
def read(name):
    with (root/'evidence'/name).open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))
rules = read('selected_rules.csv')
lookup = {(r['A'],r['B']): r for r in read('all_pair_rules.csv')}

fig, ax = plt.subplots(figsize=(8,2.45))
labels=['Tableau to SQL','Problem solving to communication','Process improvement to project management','Project management to communication']
pairs=[('tableau','sql'),('problem solving','communication'),('process improvement','project management'),('project management','communication')]
values=[float(lookup[p]['lift']) for p in pairs]
ax.barh(labels[::-1],values[::-1],color='#31566c',height=.55)
ax.axvline(1,color='#777777',linestyle='--',linewidth=1)
for i,value in enumerate(values[::-1]): ax.text(value+.04,i,f'{value:.2f}',va='center',fontsize=10)
ax.set_xlim(0,4);ax.set_xlabel('Lift');ax.spines[['top','right','left']].set_visible(False)
fig.tight_layout();fig.savefig(root/'evidence'/'selected_lift.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(14,3.25),dpi=240)
fig.patch.set_facecolor('white'); ax.set(xlim=(0,14),ylim=(0,3.25));ax.axis('off')
navy='#254B60';grey='#637889';light='#F1F5F8';teal='#176A79';line='#9BAEB9'
def box(x,y,w,h,title,sub=None,active=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.10',facecolor=teal if active else light,edgecolor=teal if active else '#CED9E0',linewidth=1.1))
    ax.text(x+w/2,y+h*(.65 if sub else .5),title,ha='center',va='center',fontsize=12.5,fontweight='bold',color='white' if active else navy)
    if sub: ax.text(x+w/2,y+h*.30,sub,ha='center',va='center',fontsize=10.5,color='white' if active else grey)
def arrow(a,b,color=line):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,lw=1.25,color=color,shrinkA=0,shrinkB=0))
for x,label in [(1.35,'01  DATA SOURCES'),(4.45,'02  PREPARATION'),(8.0,'03  ANALYSIS'),(12.2,'04  REPORTING')]:
    ax.text(x,3.08,label,ha='center',va='center',fontsize=10,fontweight='bold',color=grey)
box(.15,1.1,2.4,1.0,'Postings & skills','Two source CSVs')
box(3.1,1.1,2.7,1.,'Join · Filter · Normalise','Shared analytical cohort')
arrow((2.55,1.6),(3.05,1.6))
ys=[2.34,1.66,.98,.30]
labels=[('AQ1','Employers'),('AQ2','Skill co-occurrence'),('AQ3','Regions'),('AQ4','Job titles')]
ax.plot([6.18,6.18],[.59,2.63],c=line,lw=1.2);ax.plot([5.8,6.18],[1.6,1.6],c=line,lw=1.2)
for y,(aq,lab) in zip(ys,labels):
    box(6.65,y,2.95,.57,aq+'  |  '+lab,active=aq=='AQ2')
    arrow((6.18,y+.285),(6.60,y+.285),teal if aq=='AQ2' else line)
    ax.plot([9.62,10.1],[y+.285,y+.285],c=teal if aq=='AQ2' else line,lw=1.2)
ax.plot([10.1,10.1],[.585,2.625],c=line,lw=1.2)
arrow((10.1,1.6),(10.6,1.6))
box(10.65,1.1,3.1,1.,'Evaluate & report','Findings · Interpretation · Advice')
fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
fig.savefig(root/'evidence'/'workflow.png',facecolor='white',dpi=240)
plt.close(fig)
