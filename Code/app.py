import sys
from pathlib import Path

import streamlit as st


# =============================================================
# PROJECT PATH
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = PROJECT_ROOT / "Code"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))


# =============================================================
# IMPORT RAG COMPONENTS
# =============================================================

from retrieval.search import load_retriever, search

from rag.rag_answer import (
    create_prompt,
    generate_answer,
    calculate_confidence,
    evidence_is_sufficient,
    OLLAMA_MODEL,
    TOP_K,
)


# =============================================================
# PAGE CONFIGURATION
# =============================================================

st.set_page_config(
    page_title="AUTOSAR HLD Analysis Assistant",
    page_icon="🚗",
    layout="wide"
)


# =============================================================
# LOAD RETRIEVER ONCE
# =============================================================

@st.cache_resource
def get_retriever():

    model, index, metadata = load_retriever()

    return model, index, metadata


# =============================================================
# HEADER
# =============================================================

st.title("🚗 AI-Powered AUTOSAR HLD Analysis Assistant")

st.markdown(
    """
    Analyze AUTOSAR architecture information using
    **semantic retrieval + local LLM generation**.

    The assistant retrieves relevant AUTOSAR evidence before
    generating an answer.
    """
)

st.info(
    "⚠️ AI-generated analysis only. Always verify results against "
    "the original AUTOSAR ARXML. This system does not replace "
    "engineering review or approval."
)


# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:

    st.header("System Configuration")

    st.write("**Embedding Model**")
    st.code("all-MiniLM-L6-v2")

    st.write("**Generation Model**")
    st.code(OLLAMA_MODEL)

    st.write("**Vector Database**")
    st.code("FAISS")

    st.write("**Retrieval Top-K**")
    st.write(TOP_K)

    st.divider()

    st.header("Knowledge Base")

    st.metric(
        "Source",
        "EcuExtract.arxml"
    )

    st.metric(
        "Domain",
        "AUTOSAR"
    )

    st.metric(
        "Retrieval",
        "Semantic + Reranking"
    )

    st.divider()

    st.caption(
        "Human oversight is required before using generated "
        "analysis for engineering decisions."
    )


# =============================================================
# LOAD RETRIEVER
# =============================================================

with st.spinner("Loading AUTOSAR retrieval system..."):

    model, index, metadata = get_retriever()


# =============================================================
# EXAMPLE QUESTIONS
# =============================================================

st.subheader("Ask about the AUTOSAR architecture")

example_questions = [
    "Which component provides DigitalServiceWrite?",
    "Which interface does DoorControl require through StatusLeft?",
    "What interfaces does the Door component provide?",
    "What runnable entities are present in the architecture?"
]

selected_example = st.selectbox(
    "Example questions",
    ["Select an example..."] + example_questions
)


# =============================================================
# QUESTION INPUT
# =============================================================

question = st.text_area(
    "Enter your question:",
    value=(
        ""
        if selected_example == "Select an example..."
        else selected_example
    ),
    height=100,
    placeholder=(
        "Example: Which interface does DoorControl "
        "require through StatusLeft?"
    )
)


# =============================================================
# ANALYZE BUTTON
# =============================================================

if st.button(
    "🔍 Analyze Architecture",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Retrieving AUTOSAR evidence and generating answer..."
        ):

            # -------------------------------------------------
            # RETRIEVAL
            # -------------------------------------------------

            results = search(
                question,
                model,
                index,
                metadata,
                top_k=TOP_K
            )

            # -------------------------------------------------
            # CONFIDENCE
            # -------------------------------------------------

            confidence = calculate_confidence(
                results
            )

            # -------------------------------------------------
            # EVIDENCE SUFFICIENCY
            # -------------------------------------------------

            sufficient = evidence_is_sufficient(
                results
            )

            # -------------------------------------------------
            # GENERATE ANSWER
            # -------------------------------------------------

            if sufficient:

                context_parts = []

                for result in results:

                    context_parts.append(
                        f"[Chunk ID: {result['chunk_id']}]\n"
                        f"Source: {result['source']}\n"
                        f"Chunk type: {result['chunk_type']}\n"
                        f"Evidence: {result['text']}"
                    )

                context = "\n\n".join(
                    context_parts
                )

                prompt = create_prompt(
                    question,
                    context
                )

                answer = generate_answer(
                    prompt
                )

            else:

                answer = (
                    "The provided AUTOSAR knowledge base does "
                    "not contain sufficient evidence to answer "
                    "this question."
                )


        # =====================================================
        # ANSWER
        # =====================================================

        st.subheader("Answer")

        st.write(answer)


        # =====================================================
        # CONFIDENCE
        # =====================================================

        st.subheader("Confidence")

        if confidence == "HIGH":

            st.success("🟢 HIGH")

        elif confidence == "MEDIUM":

            st.warning("🟡 MEDIUM")

        else:

            st.error("🔴 LOW")


        # =====================================================
        # RETRIEVED EVIDENCE
        # =====================================================

        st.subheader("📚 Retrieved Evidence")

        if results:

            for result in results[:3]:

                with st.expander(
                    f"{result['chunk_id']} — "
                    f"{result['source']}"
                ):

                    st.write(
                        result["text"]
                    )

        else:

            st.write(
                "No supporting evidence was retrieved."
            )


        # =====================================================
        # RETRIEVAL DETAILS
        # =====================================================

        with st.expander(
            "🔎 Retrieval Details"
        ):

            for position, result in enumerate(
                results,
                start=1
            ):

                st.markdown(
                    f"""
                    ### Result {position}

                    **Chunk:** `{result['chunk_id']}`

                    **Type:** `{result['chunk_type']}`

                    **Semantic Score:** `{result['score']:.4f}`

                    **Final Score:** `{result['final_score']:.4f}`
                    """
                )

                st.write(
                    result["text"]
                )

                st.divider()


# =============================================================
# FOOTER
# =============================================================

st.divider()

st.caption(
    "AUTOSAR HLD Analysis Assistant | "
    "RAG + FAISS + Sentence Transformers + Ollama/Mistral"
)