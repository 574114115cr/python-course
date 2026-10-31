"""把 course-code 里的 .py 逐个真跑一遍（冒烟测试）。

- 整个单元目录复制到临时目录后再跑：这样同目录依赖（calculator.py）、
  子目录（learning_logs/）都能正常 import，等于模拟学员下载整套代码。
- 环境变量：SDL_VIDEODRIVER=dummy（pygame 无头）、MPLBACKEND=Agg（matplotlib 无头）。
- stdin 给空（让 input() 立刻 EOF，不阻塞），超时 12 秒。
- 结果分类：OK / EOF(input) / MISS(缺库) / TIMEOUT / BROKEN(故意写错) / ERR。
"""
import os
import shutil
import subprocess
import sys
import tempfile

PY = sys.executable
base = sys.argv[1] if len(sys.argv) > 1 else 'course-code'
only = sys.argv[2] if len(sys.argv) > 2 else None
only_set = set(only.split(',')) if only else None

env = dict(os.environ)
env['SDL_VIDEODRIVER'] = 'dummy'
env['SDL_AUDIODRIVER'] = 'dummy'
env['MPLBACKEND'] = 'Agg'
env['PYTHONIOENCODING'] = 'utf-8'
env['PYTHONDONTWRITEBYTECODE'] = '1'

buckets = {'OK': [], 'EOF': [], 'MISS': [], 'TIMEOUT': [], 'BROKEN': [], 'ERR': []}
details = []

for unit in sorted(os.listdir(base)):
    d = os.path.join(base, unit)
    if not os.path.isdir(d) or (only_set and unit not in only_set):
        continue
    files = []
    for root, _, fs in os.walk(d):
        if os.path.basename(root) == 'snippets':
            continue
        for f in sorted(fs):
            if f.endswith('.py'):
                files.append(os.path.relpath(os.path.join(root, f), d))
    if not files:
        continue
    print('== %s（%d 个）' % (unit, len(files)))
    for rel in files:
        src = os.path.join(d, rel)
        text = open(src, encoding='utf-8').read()
        intentional = 'INTENTIONALLY' in text or 'broken' in rel.lower() or 'buggy' in rel.lower()
        tmp = tempfile.mkdtemp(prefix='ccrun-')
        try:
            work = os.path.join(tmp, 'unit')
            shutil.copytree(d, work)
            target = os.path.join(work, rel)
            r = subprocess.run([PY, target], cwd=os.path.dirname(target), env=env,
                               input='', capture_output=True, text=True, timeout=12,
                               encoding='utf-8', errors='replace')
            if r.returncode == 0:
                buckets['OK'].append(rel)
            else:
                err = r.stderr or ''
                tail = err.strip().split('\n')[-1] if err.strip() else ''
                if 'EOFError' in err:
                    buckets['EOF'].append(rel)
                elif 'ModuleNotFoundError' in err or 'ImportError' in err:
                    buckets['MISS'].append(rel)
                    details.append(('MISS', rel, tail))
                elif intentional:
                    buckets['BROKEN'].append(rel)
                else:
                    buckets['ERR'].append(rel)
                    details.append(('ERR', rel, tail))
        except subprocess.TimeoutExpired:
            buckets['TIMEOUT'].append(rel)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

print('\n════ 汇总 ════')
for k, label in [('OK', '正常退出'), ('EOF', '需要输入(EOF 结束)'),
                 ('MISS', '缺库'), ('TIMEOUT', '超时(常驻/GUI/等事件)'),
                 ('BROKEN', '故意写错(预期报错)'), ('ERR', '真实报错')]:
    print('%-22s %3d  %s' % (label, len(buckets[k]),
                             ' '.join(buckets[k][:6]) + (' …' if len(buckets[k]) > 6 else '')))
if details:
    print('\n── 需关注的明细 ──')
    for kind, rel, tail in details:
        print('[%s] %-40s %s' % (kind, rel, tail[:100]))
