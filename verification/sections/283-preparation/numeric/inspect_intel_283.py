"""Fresh bounded inspection of already downloaded official Intel primary PDF."""
from pathlib import Path
from pypdf import PdfReader
import hashlib
import json

HERE = Path(__file__).resolve().parent
PDF = HERE.parent / 'research/p2-cost-rounding-consensus-280/intel-sdm-volume2abcd-280.pdf'
SHA = 'bc4348020f5d5a27b0207c61e3c88d4e610eaf428658dc5d08a1cc84f98a719b'
raw = PDF.read_bytes()
assert hashlib.sha256(raw).hexdigest() == SHA
pdf = PdfReader(PDF)
wanted = {'CVTSI2SS', 'CVTSS2SD', 'CVTTSD2SI', 'MULSS'}
matches = []

def walk(items):
    for item in items:
        if isinstance(item, list):
            walk(item)
        else:
            title = str(item.get('/Title', ''))
            name = title.split('—', 1)[0].strip()
            if name in wanted:
                matches.append((name, title, pdf.get_destination_page_number(item)))

walk(pdf.outline)
assert {name for name, _, _ in matches} == wanted
facts = []
for name, title, index in matches:
    pages = [pdf.pages[index + d].extract_text() for d in range(2)]
    combined = '\n'.join(pages)
    if name == 'CVTSI2SS':
        assert 'MXCSR' in combined and 'quadword' in combined and 'inexact' in combined
        fact = 'Legacy REX.W signed64 integer-to-Single conversion selects the MXCSR rounding control when inexact; no actual current RC is established.'
    elif name == 'CVTTSD2SI':
        assert 'truncation' in combined and 'invalid' in combined.lower() and '80000000H' in combined
        fact = 'Legacy conversion truncates Double to the signed destination width; out-of-domain invalid behavior is not a normal usable Int32 encoder parameter. No exception-mask state is inferred.'
    elif name == 'CVTSS2SD':
        assert 'single precision' in combined.lower() and 'double precision' in combined.lower()
        fact = 'Legacy Single-to-Double conversion is represented in the instruction reference. Finite normal and zero Single values fit Double exactly; subnormal/DAZ environment is left outside this reference domain.'
    else:
        assert 'MXCSR' in combined and 'single precision' in combined.lower()
        fact = 'Legacy scalar Single multiplication follows floating arithmetic rounding. Exact normal results need no rounding choice; the FP scaling argument is separately proved from original game bytes.'
    facts.append({'instruction': name, 'bookmark': title, 'page_index': index,
                  'inspected_pages': [index, index + 1],
                  'extracted_page_sha256': [hashlib.sha256(p.encode('utf8')).hexdigest() for p in pages],
                  'fact': fact, 'full_text_or_long_quotes_archived': False})
result = {'kind': 'SECTION283_OFFICIAL_INTEL_FRESH_PRIMARY_FILE_INSPECTION',
          'url': 'https://cdrdv2-public.intel.com/774492/325383-sdm-vol-2abcd.pdf',
          'pdf_sha256': SHA, 'pdf_bytes': len(raw), 'pdf_pages': len(pdf.pages),
          'facts': facts, 'actual_mxcsr_or_exception_masks_proven': False,
          'game_dll_executed': False, 'process_memory_read': False,
          'web_open_large_pdf_failed': True,
          'web_open_failure': 'Tool refused PDF content length 11349721; verified pinned official file used instead.'}
target = HERE / 'intel-primary-inspection-283.json'
assert not target.exists(), 'preserve first actual inspection'
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'output': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                  'facts': facts}, ensure_ascii=False))
