'''
parser.py - Parse chunked markdown files into structured chunks with metadata.

Each chunked .md file follows the format defined in CHUNKING_PROTOCOL.md:
  - Header: source_id, title, authors, venue, DOI
  - Sections: ## secN -- Section Title
  - Subsections: ### secN.M -- Subsection Title
  - Chunks: [secN_pM] or [secN.M_pK] paragraph text

This module extracts each chunk as a dict with:
  - chunk_id: e.g. 'sec2.1_p3'
  - source_id: e.g. 'acciarini2021'
  - text: the paragraph content
  - section_title: the section/subsection heading
  - section_id: e.g. 'sec2.1'
'''

import re
import csv
from pathlib import Path
from typing import Optional


def parse_chunked_file(filepath: str | Path) -> list[dict]:
    '''Parse a single chunked markdown file into a list of chunk dicts.
    
    Returns:
        List of dicts, each with keys:
            source_id, chunk_id, text, section_id, section_title
    '''
    filepath = Path(filepath)
    text = filepath.read_text(encoding='utf-8')
    lines = text.split('\n')
    
    # Extract source_id from first line: '# source_id -- Title'.
    header_match = re.match(r'^#\s+(\S+)\s+--\s+(.+)', lines[0])
    if not header_match:
        raise ValueError(f'Could not parse header in {filepath}: {lines[0]}')
    source_id = header_match.group(1)
    
    chunks = []
    current_section_id = None
    current_section_title = None
    
    for line in lines:
        # Match section headers: ## secN -- Title  or  ### secN.M -- Title.
        sec_match = re.match(r'^#{2,3}\s+(sec[\d.]+)\s+--\s+(.+)', line)
        if sec_match:
            current_section_id = sec_match.group(1)
            current_section_title = sec_match.group(2).strip()
            continue
        
        # Match chunk lines: [secN_pM] text  or  [secN.M_pK] text.
        # Some chunks may have suffixes like [sec2.3_p1_1].
        chunk_match = re.match(r'^\[(sec[\d.]+_p\d+(?:_\d+)?)\]\s+(.+)', line)
        if chunk_match:
            chunk_id = chunk_match.group(1)
            chunk_text = chunk_match.group(2).strip()
            
            # Derive section_id from chunk_id (everything before _p).
            section_from_chunk = re.match(r'(sec[\d.]+)_p', chunk_id).group(1)
            
            chunks.append({
                'source_id': source_id,
                'chunk_id': chunk_id,
                'text': chunk_text,
                'section_id': section_from_chunk,
                'section_title': current_section_title or 'Unknown',
            })
    
    return chunks


def parse_header_metadata(filepath: str | Path) -> dict:
    '''Extract document-level metadata from the chunked file header.
    
    Returns:
        Dict with keys: source_id, title, authors, venue, url_or_doi
    '''
    filepath = Path(filepath)
    text = filepath.read_text(encoding='utf-8')
    lines = text.split('\n')
    
    metadata = {}
    
    # Line 0: # source_id -- Title.
    header_match = re.match(r'^#\s+(\S+)\s+--\s+(.+)', lines[0])
    if header_match:
        metadata['source_id'] = header_match.group(1)
        metadata['title'] = header_match.group(2).strip()
    
    # Subsequent lines: **Key:** Value.
    for line in lines[1:20]:  # Only scan first 20 lines.
        kv_match = re.match(r'^\*\*(.+?):\*\*\s+(.+)', line)
        if kv_match:
            key = kv_match.group(1).strip().lower()
            value = kv_match.group(2).strip()
            if key == 'authors':
                metadata['authors'] = value
            elif key == 'venue':
                metadata['venue'] = value
            elif key in ('url', 'doi'):
                metadata['url_or_doi'] = value
        if line.startswith('## '):
            break  # Stop at first section.
    
    return metadata


def load_manifest(manifest_path: str | Path) -> dict[str, dict]:
    '''Load the data_manifest.csv and return a dict keyed by source_id.

    Returns:
        Dict mapping source_id -> row dict with keys:
            title, authors, year, source_type, venue, url_or_doi,
            tags, relevance_note

    Notes:
        The CSV column ``source_type`` is stored here under the same name.
        Downstream code maps it to ``doc_type`` for ChromaDB metadata
        (see enrich_chunks_with_manifest).
    '''
    manifest_path = Path(manifest_path)
    manifest = {}

    with open(manifest_path, encoding='utf-8-sig') as f:
        # Handle potential Windows line endings.
        content = f.read().replace('\r\n', '\n').replace('\r', '\n')

    reader = csv.DictReader(content.strip().splitlines())
    for row in reader:
        sid = row['source_id'].strip()
        manifest[sid] = {
            'title': row.get('title', '').strip(),
            'authors': row.get('authors', '').strip(),
            'year': int(row.get('year', 0)),
            'source_type': row.get('source_type', '').strip(),
            'venue': row.get('venue', '').strip(),
            'url_or_doi': row.get('url_or_doi', '').strip(),
            'tags': row.get('tags', '').strip(),
            'relevance_note': row.get('relevance_note', '').strip(),
        }

    return manifest


def build_composite_id(source_id: str, chunk_id: str) -> str:
    '''Build ChromaDB document ID: source_id::chunk_id'''
    return f'{source_id}::{chunk_id}'


def enrich_chunks_with_manifest(
    chunks: list[dict], manifest: dict[str, dict]
) -> list[dict]:
    '''Merge manifest metadata into each chunk dict.

    Adds: year, doc_type, venue, authors, tags (from manifest) to each chunk.
    The manifest field ``source_type`` is stored as ``doc_type`` to match
    the existing ChromaDB metadata schema.
    '''
    for chunk in chunks:
        sid = chunk['source_id']
        if sid in manifest:
            m = manifest[sid]
            chunk['year'] = m['year']
            chunk['doc_type'] = m['source_type']
            chunk['venue'] = m['venue']
            chunk['authors'] = m['authors']
            chunk['tags'] = m.get('tags', '')
        else:
            chunk['year'] = 0
            chunk['doc_type'] = 'unknown'
            chunk['venue'] = 'unknown'
            chunk['authors'] = 'unknown'
            chunk['tags'] = ''
    return chunks
