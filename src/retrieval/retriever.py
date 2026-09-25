import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings

logger = logging.getLogger(__name__)


def load_pdf_documents(pdf_path: Path):
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()
    for doc in docs:
        meta = doc.metadata or {}
        page = meta.get('page') or meta.get('page_number') or 1
        meta['source'] = meta.get('source', str(pdf_path.name))
        meta['page'] = int(page) + 1
        doc.metadata = meta
    return docs


def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    return splitter.split_documents(docs)


def init_vector_store(force_reindex: bool = False):
    persist_dir = Path(settings.chroma_persist_directory)
    persist_dir.mkdir(parents=True, exist_ok=True)

    if not settings.pdf_path.exists():
        raise FileNotFoundError('Tesla financial report not found. Please place the PDF in the configured data directory.')

    embedding_model = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    vectordb = Chroma(
        persist_directory=str(persist_dir),
        collection_name=settings.chroma_collection,
        embedding_function=embedding_model,
    )

    try:
        existing = vectordb.get(limit=1)
        if existing and existing.get('ids') and not force_reindex:
            logger.info('Reusing existing Chroma collection.')
            return vectordb
    except Exception:
        logger.info('No valid Chroma collection found; indexing PDF.')

    docs = load_pdf_documents(settings.pdf_path)
    chunks = chunk_documents(docs)
    for idx, chunk in enumerate(chunks):
        meta = chunk.metadata or {}
        meta.setdefault('chunk_id', f'chunk_{idx}')
        meta.setdefault('source', settings.pdf_path.name)
        meta.setdefault('page', 1)
        chunk.metadata = meta

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name=settings.chroma_collection,
        persist_directory=str(persist_dir),
    )
    logger.info(f'Indexed {len(chunks)} chunks into Chroma.')
    return vectordb


def search_chunks(question: str, vector_store: Any, top_k: int = 5):
    results = vector_store.similarity_search_with_score(question, k=top_k)
    cleaned = []
    for doc, score in results:
        meta = doc.metadata or {}
        cleaned.append({
            'chunk_id': meta.get('chunk_id', 'unknown'),
            'text': doc.page_content,
            'source': meta.get('source', 'Tesla Financial Report'),
            'page': int(meta.get('page', 1)),
            'similarity_score': float(score),
        })
    return cleaned


def deduplicate_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = {}
    for chunk in chunks:
        chunk_id = chunk.get('chunk_id')
        if chunk_id not in seen or chunk.get('similarity_score', 0) > seen[chunk_id].get('similarity_score', 0):
            seen[chunk_id] = chunk
    return list(seen.values())
