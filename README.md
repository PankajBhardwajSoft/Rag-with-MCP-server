# Tesla Financial Report RAG Assistant

This project is a local Python-based RAG proof of concept for a Tesla 10-K financial report PDF. It includes a Streamlit user interface, local Chroma vector store, semantic cache, query expansion, reranking, and route-based retrieval flow.

## Quick start

1. Create and activate the local virtual environment:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
2. Install dependencies:
   python -m pip install -r requirements.txt
3. Copy `.env.example` to `.env` and add a Groq API key if available.
4. Start the app:
   streamlit run app.py

## Notes

- The app uses the Tesla PDF in the project folder.
- If no Groq API key is supplied, the app falls back to a grounded local-answer mode so the UI still works for smoke testing.
