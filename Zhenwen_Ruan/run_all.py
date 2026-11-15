import subprocess,sys
from pathlib import Path
root=Path(__file__).parent
for script in ['analyse_aq2.py','make_profiles.py','make_figures.py','verify_results.py']:
 subprocess.run([sys.executable,str(root/script)],cwd=root,check=True)
