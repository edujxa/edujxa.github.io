"""Manually publish the committed, validated dist tree to GitHub Pages."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/edujxa/edujxa.github.io.git'
AUTH = ['-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential']


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


if git('branch', '--show-current') != 'main':
    raise SystemExit('Switch to main before publishing.')
if git('status', '--porcelain', '--untracked-files=all'):
    raise SystemExit('Commit or set aside changes before publishing.')
subprocess.run([sys.executable, 'scripts/check-site.py'], cwd=ROOT, check=True)
remote_main = git(*AUTH, 'ls-remote', REPO, 'refs/heads/main').split()
if not remote_main or remote_main[0] != git('rev-parse', 'HEAD'):
    raise SystemExit('Push the reviewed main branch before publishing.')
remote_pages = git(*AUTH, 'ls-remote', REPO, 'refs/heads/gh-pages').split()
parent = []
if remote_pages:
    git(*AUTH, 'fetch', '--quiet', REPO, 'refs/heads/gh-pages')
    parent = ['-p', git('rev-parse', 'FETCH_HEAD')]
commit = git('commit-tree', 'HEAD:dist', *parent, '-m', 'Publish website')
subprocess.run(['git', *AUTH, 'push', REPO, f'{commit}:refs/heads/gh-pages'], cwd=ROOT, check=True)
print('Published branch updated. GitHub Pages deployment may take a few minutes.')
