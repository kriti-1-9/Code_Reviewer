# The 24/7 Intelligent Code Reviewer

**Automated, always-on intelligent code reviewer for the next generation of engineers.**

Multi-language reviews • Quality scoring • Historical learning

Built with Gemini (Vertex AI) + Firestore + Cloud Run.

---

## Why this exists

Human code reviews are slow, inconsistent, and often unavailable. Junior and AI-generated code introduces subtle bugs and security issues. Team knowledge about past mistakes gets lost.

This service gives every engineer an instant, consistent first-pass review with a clear quality score — and it gets smarter over time by learning from previous findings and human feedback.

## Features

- **Multi-language** – Python, JavaScript/TypeScript, Go, Java, Rust, C++, and more
- **Quality Rating** – Overall score (0–100) + breakdown across correctness, security, performance, maintainability, and style
- **Actionable findings** – Severity-ranked issues with concrete suggestions
- **Historical Learning** – Past reviews and human feedback influence future reviews
- **Always-on** – Ready for Cloud Run + GitHub webhooks / CLI / API

## Architecture

"""PR / CLI / API  →  Cloud Run (FastAPI)
↓
Gemini (Vertex AI)  ← historical context from Firestore
↓
Structured review + quality score
↓
Store in Firestore (+ optional PR comments)"""


## Quick Start (Local)

```bash
# 1. Clone & setup
git clone https://github.com/YOUR_USERNAME/24-7-intelligent-code-reviewer.git
cd 24-7-intelligent-code-reviewer

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env → set GCP_PROJECT_ID

# 3. Authenticate with GCP
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# 4. Run
uvicorn app.main:app --reload --port 8080