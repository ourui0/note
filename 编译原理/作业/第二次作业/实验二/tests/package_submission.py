"""Package only required files, then test a fresh extraction of the actual ZIP."""
from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile
import time
import zipfile
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
SUBMISSION=ROOT/'proj2_submission'
ARCHIVE=ROOT/'proj2_submission.zip'
names=['Code/parser.h','Code/lexer.l','Code/parser.y','Code/parser.c',
       'Code/semantic.h','Code/semantic.c','report.pdf']
pdf=PdfReader(SUBMISSION/'report.pdf')
assert 1 <= len(pdf.pages) <= 3
sizes=[]
for page in pdf.pages:
    page.extract_text(visitor_text=lambda text,cm,tm,font,size: sizes.append(size) if text.strip() else None)
assert min(sizes)>=11, min(sizes)
content='\n'.join(page.extract_text() for page in pdf.pages)
assert '2.3' in content and 'semantic.c' in content and 'gcc -std=c99' in content

# Equal timestamps prevent make's built-in yacc rule from overwriting parser.c.
stamp=time.localtime()[:6]
with zipfile.ZipFile(ARCHIVE,'w',zipfile.ZIP_DEFLATED) as archive:
    directory=zipfile.ZipInfo('Code/',stamp)
    directory.external_attr=(0o40755<<16)|0x10
    archive.writestr(directory,b'')
    for name in names:
        info=zipfile.ZipInfo(name,stamp)
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o100644<<16
        archive.writestr(info,(SUBMISSION/name).read_bytes())
with zipfile.ZipFile(ARCHIVE) as archive:
    assert archive.testzip() is None
    assert archive.namelist()==['Code/']+names
    with tempfile.TemporaryDirectory(prefix='lab2-package-') as temp:
        archive.extractall(temp)
        subprocess.run([sys.executable,str(ROOT/'tests/run_tests.py'),str(Path(temp)/'Code')],check=True)
print(f'PDF: {len(pdf.pages)} pages, minimum font {min(sizes):g} pt')
print('ZIP verified:',ARCHIVE)
print('SHA256:',hashlib.sha256(ARCHIVE.read_bytes()).hexdigest())
