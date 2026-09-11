"""Gemini-powered code review engine."""

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from app.config import GCP_PROJECT_ID, GCP_LOCATION, GEMINI_MODEL
from app.models import CodeSnippet, Finding, QualityScore, ReviewResponse


SYSTEM_PROMPT = """You are an expert multi-language code reviewer for modern engineering teams.
Analyze the provided code (or diff) and return a STRICT JSON object only (no markdown).

Required JSON schema:
{
  "language": "detected language",
  "quality": {
    "overall": 0-100,
    "correctness": 0-100,
    "security": 0-100,
    "performance": 0-100,
    "maintainability": 0-100,
    "style": 0-100
  },
  "findings": [
    {
      "severity": "critical|high|medium|low|suggestion",
      "category": "security|correctness|performance|maintainability|style",
      "line": null or integer,
      "message": "clear problem description",
      "suggestion": "concrete fix or null"
    }
  ],
  "summary": "2-4 sentence executive summary"
}

Rules:
- Be precise and actionable. Prefer fewer high-signal findings over noise.
- Flag real security issues (injection, secrets, auth, XSS, etc.).
- Consider language-specific best practices.
- If historical context is provided, prefer patterns that were previously accepted and avoid repeating dismissed issues.
- Overall score should reflect severity and density of issues.
"""


class GeminiReviewer:
    def __init__(self):
        if GCP_PROJECT_ID:
            vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
        self.model = GenerativeModel(GEMINI_MODEL)

    def review(
        self,
        code: CodeSnippet,
        historical_context: Optional[str] = None,
        extra_context: Optional[str] = None,
    ) -> ReviewResponse:
        user_parts = []
        if code.filename:
            user_parts.append(f"Filename: {code.filename}")
        if code.language:
            user_parts.append(f"Claimed language: {code.language}")
        if code.diff:
            user_parts.append("### Diff\n```\n" + code.diff + "\n```")
        user_parts.append("### Code\n```\n" + code.content + "\n```")

        if historical_context:
            user_parts.append(
                "### Relevant historical findings & team conventions\n" + historical_context
            )
        if extra_context:
            user_parts.append("### Extra context\n" + extra_context)

        prompt = "\n\n".join(user_parts)

        generation_config = GenerationConfig(
            temperature=0.2,
            max_output_tokens=4096,
            response_mime_type="application/json",
        )

        response = self.model.generate_content(
            [SYSTEM_PROMPT, prompt],
            generation_config=generation_config,
        )

        raw = response.text.strip()
        # Safety: strip accidental markdown fences
        raw = re.sub(r"^```json\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

        data = json.loads(raw)

        quality = QualityScore(**data["quality"])
        findings = [Finding(**f) for f in data.get("findings", [])]

        return ReviewResponse(
            review_id=str(uuid.uuid4()),
            language=data.get("language", code.language or "unknown"),
            quality=quality,
            findings=findings,
            summary=data.get("summary", ""),
            created_at=datetime.now(timezone.utc),
        )