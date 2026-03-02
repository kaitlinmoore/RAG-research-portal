'''
ingest.py - Ingest chunked markdown files into ChromaDB with embeddings.

Usage:
    python -m src.ingest.ingest \
        --chunks-dir data/processed \
        --manifest data_manifest.csv \
        --db-path data/chromadb \
        --collection space_debris_rag

Workflow:
    1. Discover all *_chunked.md files in --chunks-dir.
    2. Parse each file into chunks with metadata (parser.py).
    3. Enrich with manifest metadata (year, source_type, venue, tags).
    4. Generate embeddings using sentence-transformers/all-mpnet-base-v2.
    5. Upsert into ChromaDB collection with metadata.

Requirements:
    pip install chromadb sentence-transformers

ChromaDB metadata schema per chunk:
    - source_id:      str   e.g. 'acciarini2021'
    - chunk_id:       str   e.g. 'sec2.1_p3'
    - section_id:     str   e.g. 'sec2.1'
    - section_title:  str   e.g. 'Bayesian machine learning'
    - year:           int   e.g. 2021
    - doc_type:       str   e.g. 'peer-reviewed'
    - venue:          str   e.g. 'Acta Astronautica'
    - authors:        str   e.g. 'Giacomo Acciarini, Francesco Pinto, ...'
    - tags:           str   e.g. 'collision-avoidance; data-quality' (display only)
    - tag_collision_avoidance:        bool
    - tag_orbit_prediction:           bool
    - tag_debris_environment:         bool
    - tag_detection_classification:   bool
    - tag_data_quality:               bool
    - tag_generalization:             bool
    - tag_uncertainty_quantification: bool
    - tag_operational_integration:    bool
    - tag_survey:                     bool
    - tag_benchmark:                  bool
    - tag_policy:                     bool
'''

# All 11 tags — used to generate boolean metadata fields from the
# semicolon-separated tags string in the manifest.
ALL_TAGS = [
    "collision-avoidance",
    "orbit-prediction",
    "debris-environment",
    "detection-classification",
    "data-quality",
    "generalization",
    "uncertainty-quantification",
    "operational-integration",
    "survey",
    "benchmark",
    "policy",
]


def _tag_booleans(tags_str: str) -> dict[str, bool]:
    """Convert a semicolon-separated tags string to boolean fields.

    E.g. "collision-avoidance; data-quality" →
         {"tag_collision_avoidance": True, "tag_data_quality": True, ...rest False}
    """
    present = {t.strip() for t in tags_str.split(";") if t.strip()}
    return {
        f"tag_{tag.replace('-', '_')}": (tag in present)
        for tag in ALL_TAGS
    }

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path so we can import parser.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.ingest.parser import (
    parse_chunked_file,
    load_manifest,
    enrich_chunks_with_manifest,
    build_composite_id,
)

# I chose this model as a higher performance option which shouldn't be too slow with a corpus this size.
# I do have the argument to allow testing with other models if needed.
def get_embedding_function(model_name: str = 'all-mpnet-base-v2'):
    '''Load sentence-transformers model and return a ChromaDB-compatible 
    embedding function.
    
    Args:
        model_name: HuggingFace model name for sentence-transformers
    
    Returns:
        chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction
    '''
    from chromadb.utils.embedding_functions import (
        SentenceTransformerEmbeddingFunction,
    )
    
    print(f'Loading embedding model: {model_name}')
    ef = SentenceTransformerEmbeddingFunction(model_name=model_name)
    print('Embedding model loaded.')
    return ef


def discover_chunked_files(chunks_dir: Path) -> list[Path]:
    '''Find all *_chunked.md files in the given directory.'''
    files = sorted(chunks_dir.glob('*_chunked.md'))
    print(f'Found {len(files)} chunked files in {chunks_dir}')
    return files


def ingest(
    chunks_dir: str | Path,
    manifest_path: str | Path,
    db_path: str | Path = 'data/chromadb',
    collection_name: str = 'space_debris_rag',
    model_name: str = 'all-mpnet-base-v2',
    batch_size: int = 50,
):
    '''Main ingest pipeline.
    
    Args:
        chunks_dir:      Directory containing *_chunked.md files
        manifest_path:   Path to data_manifest.csv
        db_path:         Directory for ChromaDB persistent storage
        collection_name: Name of the ChromaDB collection
        model_name:      Sentence-transformers model name
        batch_size:      Number of chunks to upsert per batch
    '''
    import chromadb
    
    chunks_dir = Path(chunks_dir)
    manifest_path = Path(manifest_path)
    db_path = Path(db_path)
    
    # 1. Load manifest.
    print('Loading manifest...')
    manifest = load_manifest(manifest_path)
    print(f'  Manifest contains {len(manifest)} sources')
    
    # 2. Discover chunked files.
    chunked_files = discover_chunked_files(chunks_dir)
    if not chunked_files:
        print('No chunked files found. Exiting.')
        return
    
    # 3. Parse all chunks.
    all_chunks = []
    for fp in chunked_files:
        try:
            chunks = parse_chunked_file(fp)
            chunks = enrich_chunks_with_manifest(chunks, manifest)
            all_chunks.extend(chunks)
            print(f'  Parsed {fp.name}: {len(chunks)} chunks')
        except Exception as e:
            print(f'  ERROR parsing {fp.name}: {e}')
    
    print(f'\nTotal chunks to ingest: {len(all_chunks)}')
    
    # 4. Set up ChromaDB.
    print(f'\nInitializing ChromaDB at {db_path}...')
    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))
    
    # 5. Load embedding function.
    ef = get_embedding_function(model_name)
    
    # 6. Create or get collection.
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={'hnsw:space': 'cosine'},  # cosine similarity
    )
    print(f'Collection "{collection_name}" ready (existing count: {collection.count()})')
    
    # 7. Prepare and upsert in batches.
    ids = []
    documents = []
    metadatas = []
    
    for chunk in all_chunks:
        composite_id = build_composite_id(chunk['source_id'], chunk['chunk_id'])
        ids.append(composite_id)
        documents.append(chunk['text'])
        tags_str = chunk.get('tags', '')
        meta = {
            'source_id': chunk['source_id'],
            'chunk_id': chunk['chunk_id'],
            'section_id': chunk['section_id'],
            'section_title': chunk['section_title'],
            'year': chunk['year'],
            'doc_type': chunk['doc_type'],
            'venue': chunk['venue'],
            'authors': chunk['authors'],
            'tags': tags_str,
        }
        meta.update(_tag_booleans(tags_str))
        metadatas.append(meta)
    
    # Upsert in batches.
    total = len(ids)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        collection.upsert(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )
        print(f'  Upserted batch {start+1}-{end} of {total}')
    
    print(f'\nIngestion complete. Collection now has {collection.count()} chunks.')
    
    # 8. Quick sanity check
    print('\n--- Sanity Check ---')
    results = collection.query(
        query_texts=['collision avoidance machine learning'],
        n_results=3,
    )
    for i, (doc_id, doc, dist) in enumerate(
        zip(results['ids'][0], results['documents'][0], results['distances'][0])
    ):
        print(f'  [{i+1}] {doc_id} (dist={dist:.4f})')
        print(f'      {doc[:120]}...')
    

def main():
    parser = argparse.ArgumentParser(
        description='Ingest chunked markdown files into ChromaDB'
    )
    parser.add_argument(
        '--chunks-dir',
        type=str,
        default='data/processed',
        help='Directory containing *_chunked.md files',
    )
    parser.add_argument(
        '--manifest',
        type=str,
        default='data_manifest.csv',
        help='Path to data_manifest.csv',
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='data/chromadb',
        help='Directory for ChromaDB persistent storage',
    )
    parser.add_argument(
        '--collection',
        type=str,
        default='space_debris_rag',
        help='ChromaDB collection name',
    )
    parser.add_argument(
        '--model',
        type=str,
        default='all-mpnet-base-v2',
        help='Sentence-transformers embedding model name',
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Batch size for ChromaDB upserts',
    )
    
    args = parser.parse_args()
    
    ingest(
        chunks_dir=args.chunks_dir,
        manifest_path=args.manifest,
        db_path=args.db_path,
        collection_name=args.collection,
        model_name=args.model,
        batch_size=args.batch_size,
    )


if __name__ == '__main__':
    main()
