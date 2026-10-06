import sys
from pathlib import Path

import streamlit as st


# =============================================================
# PROJECT PATH
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAG_DIR = PROJECT_ROOT / "Code" / "rag"

if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))


# =============================================================
# IMPORT RAG PIPELINE
# =============================================================

from rag_pipeline import (
    answer_question,
    OLLAMA_MODEL,
    TOP_K
)


# =============================================================
# STREAMLIT CONFIGURATION
# =============================================================

st.set_page_config(
    page_title="AUTOSAR HLD Analysis Assistant",
    page_icon="🚗",
    layout="wide"
)


# =============================================================
# TITLE
# =============================================================

st.title(
    "🚗 AI-Powered AUTOSAR HLD Analysis Assistant"
)

st.caption(
    "Grounded RAG system for AUTOSAR architecture analysis"
)


st.info(
    "AI-generated analysis is intended to assist engineers. "
    "Always verify results against the original AUTOSAR ARXML."
)


# =============================================================
# RETRIEVER
# =============================================================

@st.cache_resource
def load_retrieval_system():

    retrieval_dir = (
        PROJECT_ROOT
        / "Code"
        / "retrieval"
    )

    if str(retrieval_dir) not in sys.path:
        sys.path.insert(
            0,
            str(retrieval_dir)
        )

    from search import load_retriever

    return load_retriever()


# =============================================================
# LOAD RETRIEVER
# =============================================================

with st.spinner(
    "Loading AUTOSAR knowledge base..."
):

    model, index, metadata = (
        load_retrieval_system()
    )


# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:

    st.header("System Configuration")

    st.write(
        f"**Embedding Model:** "
        f"`all-MiniLM-L6-v2`"
    )

    st.write(
        f"**Generation Model:** "
        f"`{OLLAMA_MODEL}`"
    )

    st.write(
        f"**Vector Database:** "
        f"`FAISS`"
    )

    st.write(
        f"**Retrieval Top-K:** "
        f"`{TOP_K}`"
    )

    st.write(
        f"**Indexed Chunks:** "
        f"`{index.ntotal}`"
    )

    st.divider()

    st.subheader(
        "Knowledge Base"
    )

    st.write(
        "`EcuExtract.arxml`"
    )

    st.divider()

    st.subheader(
        "Responsible AI"
    )

    st.write(
        "The assistant provides grounded "
        "analysis from the AUTOSAR knowledge "
        "base and does not replace engineering "
        "review or approval."
    )


# =============================================================
# EXAMPLE QUESTIONS
# =============================================================

st.subheader(
    "Example Questions"
)

example_questions = [
    "Which component provides DigitalServiceWrite?",
    "Which interface does DoorControl require through StatusLeft?",
    "What interfaces does the Door component provide?",
    "What runnable entities are present in the architecture?"
]


selected_example = st.selectbox(
    "Select an example:",
    ["-- Select --"] + example_questions
)


# =============================================================
# QUESTION INPUT
# =============================================================

question = st.text_area(
    "Enter your AUTOSAR architecture question:",
    value=(
        selected_example
        if selected_example != "-- Select --"
        else ""
    ),
    height=100,
    placeholder=(
        "Example: Which interface does "
        "DoorControl require through StatusLeft?"
    )
)


# =============================================================
# ANALYZE BUTTON
# =============================================================

if st.button(
    "🔍 Analyze AUTOSAR Architecture",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Retrieving evidence and generating grounded answer..."
        ):

            try:

                result = answer_question(
                    question,
                    model,
                    index,
                    metadata,
                    top_k=TOP_K
                )

            except Exception as error:

                st.error(
                    f"Pipeline error: {error}"
                )

            else:

                # -------------------------------------------------
                # ANSWER
                # -------------------------------------------------

                st.subheader(
                    "Answer"
                )

                st.write(
                    result["answer"]
                )


                # -------------------------------------------------
                # CONFIDENCE
                # -------------------------------------------------

                st.subheader(
                    "Confidence"
                )

                confidence = (
                    result["confidence"]
                )

                if confidence == "HIGH":

                    st.success(
                        f"🟢 {confidence}"
                    )

                elif confidence == "MEDIUM":

                    st.warning(
                        f"🟡 {confidence}"
                    )

                else:

                    st.error(
                        f"🔴 {confidence}"
                    )


                # -------------------------------------------------
                # EVIDENCE STATUS
                # -------------------------------------------------

                if result[
                    "evidence_sufficient"
                ]:

                    st.success(
                        "Sufficient AUTOSAR evidence "
                        "was retrieved for this answer."
                    )

                else:

                    st.warning(
                        "The knowledge base does not "
                        "contain sufficient evidence "
                        "for this question."
                    )


                # -------------------------------------------------
                # RETRIEVED EVIDENCE
                # -------------------------------------------------

                st.subheader(
                    "Retrieved Evidence"
                )

                for i, evidence in enumerate(
                    result["citations"],
                    start=1
                ):

                    with st.expander(
                        f"Evidence {i} — "
                        f"{evidence['chunk_id']}"
                    ):

                        st.write(
                            f"**Source:** "
                            f"{evidence['source']}"
                        )

                        st.write(
                            f"**Chunk Type:** "
                            f"{evidence['chunk_type']}"
                        )

                        st.write(
                            evidence["text"]
                        )


                # -------------------------------------------------
                # RETRIEVAL DETAILS
                # -------------------------------------------------

                with st.expander(
                    "Retrieval Details"
                ):

                    for i, item in enumerate(
                        result["results"],
                        start=1
                    ):

                        st.write(
                            f"**Rank {i}**"
                        )

                        st.write(
                            f"Chunk: "
                            f"`{item['chunk_id']}`"
                        )

                        st.write(
                            f"Semantic Score: "
                            f"{item['score']:.4f}"
                        )

                        st.write(
                            f"Final Score: "
                            f"{item['final_score']:.4f}"
                        )

                        st.write(
                            f"Type: "
                            f"{item['chunk_type']}"
                        )

                        st.divider()


# =============================================================
# FOOTER
# =============================================================

st.divider()

st.caption(
    "AI-Powered AUTOSAR HLD Analysis Assistant | "
    "RAG + FAISS + Ollama/Mistral"
)