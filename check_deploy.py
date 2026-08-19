import os

checks = []

# 1. All required files exist
required = [
    'app/main.py', 'app/config.py', 'app/security.py',
    'app/webull_client.py', 'app/routers/market.py',
    'app/routers/trade.py', 'app/__init__.py',
    'app/routers/__init__.py', 'server.py',
    'requirements.txt', 'Dockerfile',
    '.gitignore', '.dockerignore',
]
for f in required:
    if os.path.exists(f):
        checks.append(('OK', f'File exists: {f}'))
    else:
        checks.append(('FAIL', f'MISSING FILE: {f}'))

# 2. venv excluded from docker image
with open('.dockerignore', encoding='utf-8') as f:
    di = f.read()
checks.append(('OK' if 'venv/' in di else 'FAIL',
               'venv/ excluded from Docker image' if 'venv/' in di else 'venv/ NOT in .dockerignore'))

# 3. conf/token.txt excluded from git
with open('.gitignore', encoding='utf-8') as f:
    gi = f.read()
checks.append(('OK' if 'conf/token.txt' in gi else 'FAIL',
               'conf/token.txt excluded from git' if 'conf/token.txt' in gi else 'conf/token.txt NOT in .gitignore – token will leak!'))

# 4. No real key in getToken.py
with open('getToken.py', encoding='utf-8') as f:
    gt = f.read()
checks.append(('OK' if '<your_app_key>' in gt else 'WARN',
               'getToken.py has placeholder values only' if '<your_app_key>' in gt else 'getToken.py may have real credentials'))

# 5. CORS no trailing slash
with open('app/main.py', encoding='utf-8') as f:
    mn = f.read()
ok = 'doi-again.vercel.app"' in mn and 'doi-again.vercel.app/"' not in mn
checks.append(('OK' if ok else 'FAIL',
               'CORS origin has no trailing slash' if ok else 'CORS origin still has trailing slash'))

# 6. Dockerfile uses $PORT
with open('Dockerfile', encoding='utf-8') as f:
    df = f.read()
ok = 'PORT:-8000' in df
checks.append(('OK' if ok else 'FAIL',
               'Dockerfile uses $PORT env var' if ok else 'Dockerfile does not use $PORT'))

# 7. requirements.txt has webull SDK
with open('requirements.txt', encoding='utf-8') as f:
    req = f.read()
for pkg in ['fastapi', 'uvicorn', 'gunicorn', 'webull-openapi-python-sdk', 'pydantic']:
    checks.append(('OK' if pkg in req else 'FAIL',
                   f'{pkg} in requirements.txt' if pkg in req else f'{pkg} MISSING from requirements.txt'))

# ── Print report ──────────────────────────────────────────────────────────────
print('=' * 58)
print('   DEPLOYMENT READINESS CHECK')
print('=' * 58)
for status, msg in checks:
    icon = ' OK  ' if status == 'OK' else (' WARN' if status == 'WARN' else ' FAIL')
    print(f'  [{icon}] {msg}')

fails = [c for c in checks if c[0] == 'FAIL']
warns = [c for c in checks if c[0] == 'WARN']
print('=' * 58)
if not fails:
    suffix = ' (1 warning)' if warns else ''
    print(f'  RESULT: READY TO DEPLOY{suffix}')
else:
    print(f'  RESULT: {len(fails)} issue(s) must be fixed')
