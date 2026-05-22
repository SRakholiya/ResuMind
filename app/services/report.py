"""Generate a styled PDF report from analysis results."""
import io
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.lib.enums import TA_LEFT


PRIMARY = colors.HexColor("#4f46e5")  # indigo
ACCENT = colors.HexColor("#10b981")   # emerald
MUTED = colors.HexColor("#6b7280")
LIGHT_BG = colors.HexColor("#f3f4f6")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontSize=22,
                                textColor=PRIMARY, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontSize=10,
                                   textColor=MUTED, spaceAfter=12),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontSize=14,
                             textColor=PRIMARY, spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=10.5,
                               leading=15, alignment=TA_LEFT),
        "bullet": ParagraphStyle("bullet", parent=base["BodyText"], fontSize=10.5,
                                 leading=15, leftIndent=14, bulletIndent=2),
        "score_big": ParagraphStyle("score_big", parent=base["Title"], fontSize=42,
                                    textColor=PRIMARY, alignment=1),
        "score_label": ParagraphStyle("score_label", parent=base["Normal"], fontSize=9,
                                      textColor=MUTED, alignment=1),
    }


def _bullet_list(items, style):
    if not items:
        return [Paragraph("<i>None reported.</i>", style)]
    return [Paragraph(f"• {item}", style) for item in items]


def build_pdf(analysis: dict, ats: dict | None = None) -> bytes:
    """Build a PDF in memory and return its bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title="AI Resume Analysis Report",
    )
    s = _styles()
    story = []

    # Header
    story.append(Paragraph("AI Resume Analysis Report", s["title"]))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        s["subtitle"],
    ))

    # Score panel
    score = int(analysis.get("score", 0))
    sim = ats.get("similarity_pct") if ats else None

    score_cells = [[
        Paragraph(f"{score}<font size=20>/100</font>", s["score_big"]),
        Paragraph(f"{sim}%" if sim is not None else "—", s["score_big"]),
    ], [
        Paragraph("AI Match Score", s["score_label"]),
        Paragraph("ATS Similarity (TF-IDF)", s["score_label"]),
    ]]
    score_table = Table(score_cells, colWidths=[3.4 * inch, 3.4 * inch])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    # Verdict + summary
    verdict = analysis.get("verdict") or ""
    summary = analysis.get("summary") or ""
    if verdict:
        story.append(Paragraph(f"<b>Verdict:</b> {verdict}", s["body"]))
    if summary:
        story.append(Paragraph(summary, s["body"]))

    # Section scores
    section_scores = analysis.get("section_scores") or []
    if section_scores:
        story.append(Paragraph("Section Breakdown", s["h2"]))
        rows = [["Section", "Score", "Note"]]
        for item in section_scores:
            rows.append([
                str(item.get("section", "")),
                f"{item.get('score', 0)}/5",
                Paragraph(str(item.get("note", "")), s["body"]),
            ])
        t = Table(rows, colWidths=[1.6 * inch, 0.8 * inch, 4.4 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t)

    # Strengths / weaknesses (no emoji — default Helvetica lacks color glyphs)
    story.append(Paragraph("Strengths", s["h2"]))
    story.extend(_bullet_list(analysis.get("strengths", []), s["bullet"]))

    story.append(Paragraph("Weaknesses", s["h2"]))
    story.extend(_bullet_list(analysis.get("weaknesses", []), s["bullet"]))

    # Missing keywords (combine AI + ATS)
    ai_missing = analysis.get("missing_keywords", []) or []
    ats_missing = (ats or {}).get("missing_keywords", []) or []
    combined = list(dict.fromkeys([*ai_missing, *ats_missing]))[:20]
    if combined:
        story.append(Paragraph("Missing / Recommended Keywords", s["h2"]))
        story.append(Paragraph(", ".join(combined), s["body"]))

    # Suggestions
    story.append(Paragraph("Suggestions to Improve", s["h2"]))
    story.extend(_bullet_list(analysis.get("suggestions", []), s["bullet"]))

    def _footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#9ca3af"))
        canvas.drawCentredString(
            LETTER[0] / 2.0, 0.4 * inch,
            "Generated by ResuMind  ·  Informational only — does not guarantee job outcomes."
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()

