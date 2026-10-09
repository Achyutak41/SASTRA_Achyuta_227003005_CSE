
import unittest
from unittest.mock import patch

from app.rag_service import (
    answer_question,
    build_evidence_context,
)


class RagServiceTests(unittest.TestCase):

    def setUp(self):
        self.sources = [{
            "document_id": 53,
            "filename": "AUTOSAR_EXP_LayeredSoftwareArchitecture.pdf",
            "chunk_id": 101,
            "page_number": 18,
            "section_title": "AUTOSAR Runtime Environment (RTE)",
            "text": (
                "The RTE provides communication services "
                "to AUTOSAR application software components."
            ),
            "similarity_score": 0.67,
            "rerank_score": 6.02,
        }]

    def test_build_evidence_context(self):
        context, citations = build_evidence_context(self.sources)

        self.assertIn("SOURCE [1]", context)
        self.assertIn("page 18", context)
        self.assertIn("communication services", context)
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["label"], "[1]")

    @patch("app.rag_service.generate_completion")
    @patch("app.rag_service.search_document")
    def test_answer_question(self, mock_search, mock_generate):
        mock_search.return_value = self.sources
        mock_generate.return_value = {
            "answer": "The RTE provides communication services [1].",
            "model": "qwen2.5:3b",
            "prompt_eval_count": 100,
            "eval_count": 20,
            "total_duration": 1000000,
        }

        result = answer_question(
            document_id=53,
            user_id=1,
            question="What does the RTE do?",
        )

        self.assertIn("[1]", result["answer"])
        self.assertEqual(result["model"], "qwen2.5:3b")
        self.assertEqual(result["retrieved_count"], 1)
        self.assertEqual(result["citations"][0]["page_number"], 18)
        mock_search.assert_called_once()
        mock_generate.assert_called_once()

    @patch("app.rag_service.generate_completion")
    @patch("app.rag_service.search_document")
    def test_no_evidence(self, mock_search, mock_generate):
        mock_search.return_value = []

        result = answer_question(
            document_id=53,
            user_id=1,
            question="What does the RTE do?",
        )

        self.assertEqual(result["citations"], [])
        self.assertEqual(result["retrieved_count"], 0)
        self.assertIn("couldn't find", result["answer"].lower())
        mock_generate.assert_not_called()

    def test_empty_question_rejected(self):
        with self.assertRaises(ValueError):
            answer_question(
                document_id=53,
                user_id=1,
                question="   ",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
