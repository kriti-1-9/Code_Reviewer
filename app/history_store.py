"""Firestore-backed historical learning store."""

from typing import List, Optional
from datetime import datetime, timezone

from google.cloud import firestore

from app.config import GCP_PROJECT_ID, FIRESTORE_COLLECTION
from app.models import ReviewResponse, FeedbackRequest


class HistoryStore:
    def __init__(self):
        self.db = firestore.Client(project=GCP_PROJECT_ID) if GCP_PROJECT_ID else None
        self.collection = FIRESTORE_COLLECTION

    def save_review(
        self,
        review: ReviewResponse,
        code_snippet: str,
        filename: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> str:
        if not self.db:
            return review.review_id

        doc_ref = self.db.collection(self.collection).document(review.review_id)
        doc_ref.set(
            {
                "review_id": review.review_id,
                "language": review.language,
                "filename": filename,
                "repo": repo,
                "code_preview": code_snippet[:2000],
                "quality": review.quality.model_dump(),
                "findings": [f.model_dump() for f in review.findings],
                "summary": review.summary,
                "created_at": review.created_at.isoformat(),
                "feedback": [],
            }
        )
        return review.review_id

    def add_feedback(self, feedback: FeedbackRequest) -> bool:
        if not self.db:
            return False

        doc_ref = self.db.collection(self.collection).document(feedback.review_id)
        doc = doc_ref.get()
        if not doc.exists:
            return False

        data = doc.to_dict()
        fb_list = data.get("feedback", [])
        fb_list.append(
            {
                "finding_index": feedback.finding_index,
                "action": feedback.action,
                "new_severity": feedback.new_severity,
                "comment": feedback.comment,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        doc_ref.update({"feedback": fb_list})
        return True

    def get_relevant_context(
        self,
        language: Optional[str] = None,
        filename: Optional[str] = None,
        limit: int = 5,
    ) -> str:
        """
        Simple relevance: recent reviews for same language / similar filename.
        (Can be upgraded later to true vector search with embeddings.)
        """
        if not self.db:
            return ""

        query = (
            self.db.collection(self.collection)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(20)
        )

        docs = list(query.stream())
        relevant = []

        for doc in docs:
            d = doc.to_dict()
            if language and d.get("language")