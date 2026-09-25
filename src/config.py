import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env', override=False)


class Settings:
    app_title = os.getenv('APP_TITLE', 'Tesla Financial Report RAG Assistant')
    debug = os.getenv('DEBUG', 'false').lower() == 'true'

    project_root = Path(__file__).resolve().parent.parent
    pdf_path = Path(os.getenv('PDF_PATH', str(project_root / 'data' / 'tesla_financial_report.pdf')))
    embedding_model = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    chroma_persist_directory = os.getenv('CHROMA_PERSIST_DIRECTORY', str(project_root / 'chroma_db'))
    chroma_collection = os.getenv('CHROMA_COLLECTION', 'tesla_financial_report')

    chunk_size = int(os.getenv('CHUNK_SIZE', '1000'))
    chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '150'))

    default_top_k = int(os.getenv('DEFAULT_TOP_K', '5'))
    direct_top_k = int(os.getenv('DIRECT_TOP_K', '3'))
    final_context_chunks = int(os.getenv('FINAL_CONTEXT_CHUNKS', '3'))

    reranker_model = os.getenv('RERANKER_MODEL', 'BAAI/bge-reranker-base')
    rerank_top_n = int(os.getenv('RERANK_TOP_N', '3'))

    enable_query_expansion = os.getenv('ENABLE_QUERY_EXPANSION', 'true').lower() == 'true'
    max_query_expansions = int(os.getenv('MAX_QUERY_EXPANSIONS', '3'))

    enable_semantic_cache = os.getenv('ENABLE_SEMANTIC_CACHE', 'true').lower() == 'true'
    semantic_cache_threshold = float(os.getenv('SEMANTIC_CACHE_THRESHOLD', '0.60'))
    semantic_cache_ttl_seconds = int(os.getenv('SEMANTIC_CACHE_TTL_SECONDS', '3600'))

    router_confidence_threshold = float(os.getenv('ROUTER_CONFIDENCE_THRESHOLD', '0.60'))

    groq_api_key = os.getenv('GROQ_API_KEY', '')
    groq_model = os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b')
    groq_temperature = float(os.getenv('GROQ_TEMPERATURE', '0.1'))
    groq_max_tokens = int(os.getenv('GROQ_MAX_TOKENS', '1200'))


settings = Settings()
