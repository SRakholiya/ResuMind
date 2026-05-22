"""Main HTTP routes."""
import io
from flask import Blueprint, render_template, request, jsonify, send_file, session

from app.services.extractor import extract_text
from app.services.analyzer import analyze_resume
from app.services.ats import ats_score
from app.services.report import build_pdf


bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/api/analyze")
def api_analyze():
    """Run extraction + ATS + AI analysis. Returns JSON."""
    try:
        # Get resume text — either from uploaded file OR pasted text
        resume_text = (request.form.get("resume_text") or "").strip()
        file = request.files.get("resume_file")
        if file and file.filename:
            resume_text, _ = extract_text(file)
        if not resume_text:
            return jsonify(error="Please upload a resume file or paste resume text."), 400

        job_desc = (request.form.get("job_description") or "").strip()

        # ATS score (only meaningful when JD provided; still useful to show keywords)
        ats = ats_score(resume_text, job_desc) if job_desc else {
            "similarity_pct": None,
            "matched_keywords": [],
            "missing_keywords": [],
        }

        # AI analysis
        analysis = analyze_resume(resume_text, job_desc or None)

        # Stash latest result in session so /api/report can rebuild the PDF
        session["last_result"] = {"analysis": analysis, "ats": ats}

        return jsonify(analysis=analysis, ats=ats)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=f"Server error: {e}"), 500


@bp.post("/api/report")
def api_report():
    """Generate a styled PDF report from the most recent analysis."""
    data = request.get_json(silent=True) or {}
    analysis = data.get("analysis") or (session.get("last_result") or {}).get("analysis")
    ats = data.get("ats") or (session.get("last_result") or {}).get("ats")
    if not analysis:
        return jsonify(error="No analysis available. Run an analysis first."), 400

    pdf_bytes = build_pdf(analysis, ats)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="resume-analysis.pdf",
    )
