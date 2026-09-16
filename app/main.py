"""
The 24/7 Intelligent Code Reviewer
FastAPI service ready for Cloud Run.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import ReviewRequest, ReviewResponse, FeedbackRequest
from app.gemini_reviewer import GeminiReviewer
from app.history_store import HistoryStore
from app.config import API_KEY

app = FastAPI(
    title="The 24/7 Intelligent Code Reviewer",
    description="Automated multi-language code reviews with quality scoring and historical learning",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

reviewer = GeminiReviewer()
store = HistoryStore()


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if API_KEY and API_KEY != "dev-key" and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


@app.get("/health")
def health():
    return {"status": "ok", "service": "24/7 Intelligent Code Reviewer"}


@app.post("/review", response_model=ReviewResponse)
def create_review(
    request: ReviewRequest,
    _: bool = Depends(verify_api_key),
):
    """
    Main entry point: review a code snippet or diff.
    Retrieves historical context, calls Gemini, stores the result.
    """
    try:
        historical = store.get_relevant_context(
            language=request.code.language,
            filename=request.code.filename,
        )

        result = reviewer.review(
            code=request.code,
            historical_context=historical or None,
            extra_context=request.context,
        )

        store.save_review(
            review=result,
            code_snippet=request.code.content,
            filename=request.code.filename,
            repo=request.repo,
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


@app.post("/feedback")
def submit_feedback(
    feedback: FeedbackRequest,
    _: bool = Depends(verify_api_key),
):
    """Record human feedback so the system can learn."""
    ok = store.add_feedback(feedback)
    if not ok:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "feedback recorded"}


@app.get("/")
def root():
    return {
        "name": "The 24/7 Intelligent Code Reviewer",
        "docs": "/docs",
        "endpoints": ["/health", "/review", "/feedback"],
    }