from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
src = ROOT / 'bluestock_mf_dashboard.pbix'
dst_dir = ROOT / 'dashboard'
dst = dst_dir / 'bluestock_mf.pbix'

if src.exists():
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    print('Moved', src, '->', dst)
else:
    print('Source PBIX not found at', src)
