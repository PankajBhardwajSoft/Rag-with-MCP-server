import logging

import streamlit as st

from src.config import settings
from src.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

st.set_page_config(page_title=settings.app_title, page_icon='⚡', layout='wide')

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0b1020 0%, #111827 35%, #1f2937 100%);
        color: #e5e7eb;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    [data-testid="stHeader"] {
        background: rgba(17, 24, 39, 0.8);
    }
    div[data-testid="stVerticalBlock"] > div {
        border-radius: 14px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid rgba(96, 165, 250, 0.4);
        background: rgba(15, 23, 42, 0.92);
        color: #e2e8f0;
        padding: 0.7rem 0.8rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        border-color: rgba(96, 165, 250, 0.8);
        background: rgba(30, 41, 59, 0.95);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        border: none;
        color: white;
    }
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.5);
        background: rgba(15, 23, 42, 0.7);
        color: #f8fafc;
    }
    .stExpander {
        background: rgba(15, 23, 42, 0.55);
        border-radius: 12px;
    }
    h1, h2, h3 {
        color: #f8fafc;
    }
    .caption {
        color: #93c5fd;
        font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header():
    st.title(settings.app_title)
    st.markdown('<p class="caption">Ask questions grounded in the Tesla financial report.</p>', unsafe_allow_html=True)


def render_examples():
    examples = [
        "What was Tesla's revenue?",
        "What were Tesla's major growth drivers?",
        "What risks does Tesla identify?",
        "Compare Tesla's financial performance across years.",
        "Explain Tesla's energy business strategy."
    ]
    cols = st.columns(3)
    for idx, example in enumerate(examples):
        with cols[idx % 3]:
            if st.button(example, key=f"example_{idx}"):
                st.session_state.question = example


def main():
    render_header()
    if not settings.pdf_path.exists():
        st.error('Tesla financial report not found. Please place the PDF in the configured data directory.')
        return

    if 'question' not in st.session_state:
        st.session_state.question = ''
    if 'recent_questions' not in st.session_state:
        st.session_state.recent_questions = []

    st.markdown('---')
    render_examples()

    question = st.text_area('Ask a question about the Tesla financial report...', value=st.session_state.question, height=120)
    if st.button('Ask', type='primary'):
        if not question.strip():
            st.warning('Please enter a question before running the RAG pipeline.')
            return

        with st.spinner('Running the retrieval and generation pipeline...'):
            result = run_pipeline(question)

        if result.get('error'):
            st.error(result['error'])
            return

        if result.get('answer'):
            st.subheader('Answer')
            st.markdown(result['answer'])

        sources = result.get('sources') or []
        if sources:
            st.subheader('Sources')
            for source in sources:
                st.markdown(f'- {source}')

        diagnostics = result.get('diagnostics') or {}
        if diagnostics:
            with st.expander('RAG Pipeline Details', expanded=True):
                for label, value in diagnostics.items():
                    st.write(f'{label}: {value}')

        st.session_state.recent_questions.insert(0, question)
        st.session_state.recent_questions = st.session_state.recent_questions[:5]

    if st.session_state.recent_questions:
        st.subheader('Recent questions')
        for q in st.session_state.recent_questions:
            st.write(f'- {q}')


if __name__ == '__main__':
    main()
