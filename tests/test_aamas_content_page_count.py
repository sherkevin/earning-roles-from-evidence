"""PDF fixtures for the body-page measurement used by the exact-eight gate."""
from pathlib import Path
import sys

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_aamas2027 import measure_content_pages  # noqa: E402


def _pdf(path, *, body_pages=8, mixed=False, header=True):
    doc = fitz.open()
    for number in range(body_pages):
        page = doc.new_page()
        page.insert_text((72, 120), f'Body paragraph on page {number + 1}.')
    page = doc.new_page()
    if header:
        page.insert_text((72, 65), 'Research Paper Track')
        page.insert_text((72, 755), 'AAMAS 2027 footer')
    if mixed:
        page.insert_text((72, 120), 'Discussion and Conclusion are body content.')
        page.insert_text((72, 350), 'References')
        page.insert_text((72, 380), '[1] Reference entry.')
    else:
        page.insert_text((72, 120), 'References')
        page.insert_text((72, 145), '[1] Reference entry.')
    doc.save(path)
    doc.close()


def test_mixed_body_and_references_page_counts_as_body(tmp_path):
    pdf = tmp_path / 'mixed.pdf'
    _pdf(pdf, mixed=True)
    assert measure_content_pages(pdf) == {
        'pages': 9, 'references_start_page': 9,
        'body_on_references_page': True, 'content_pages': 9,
        'conservative_content_last_page': 9,
    }


def test_clean_references_page_does_not_count_running_header_or_footer(tmp_path):
    pdf = tmp_path / 'clean.pdf'
    _pdf(pdf)
    measured = measure_content_pages(pdf)
    assert measured['body_on_references_page'] is False
    assert measured['content_pages'] == 8
    assert measured['references_start_page'] == 9


def test_no_references_counts_every_page(tmp_path):
    pdf = tmp_path / 'no_refs.pdf'
    doc = fitz.open()
    for _ in range(8):
        page = doc.new_page()
        page.insert_text((72, 120), 'Body content.')
    doc.save(pdf)
    doc.close()
    assert measure_content_pages(pdf)['content_pages'] == 8
