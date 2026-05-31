"""Render a :class:`Book` to a professionally formatted, multi-page PDF using
ReportLab. Includes a cover, copyright, table of contents, full chapter body,
diagrams (as captioned source blocks), code listings, tables and assessments.

Typography targets a standard professional layout (11.5pt body, generous
leading and margins) so that a 250-page-class book renders to a comparable
physical page count.
"""
from __future__ import annotations

import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from ..models import Book

ACCENT = colors.HexColor("#4338ca")
MUTED = colors.HexColor("#475569")


def _styles():
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=ss["Title"], fontSize=32, leading=38,
                                textColor=ACCENT, spaceAfter=18, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle", parent=ss["Normal"], fontSize=16,
                                   leading=22, textColor=MUTED, alignment=TA_CENTER,
                                   spaceAfter=12),
        "meta": ParagraphStyle("meta", parent=ss["Normal"], fontSize=11, leading=18,
                               alignment=TA_CENTER, textColor=MUTED),
        "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontSize=21, leading=26,
                             textColor=ACCENT, spaceBefore=22, spaceAfter=12),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontSize=15, leading=20,
                             textColor=colors.HexColor("#1e293b"), spaceBefore=16,
                             spaceAfter=8),
        "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontSize=12.5, leading=16,
                             textColor=colors.HexColor("#334155"), spaceBefore=10,
                             spaceAfter=4),
        "body": ParagraphStyle("body", parent=ss["BodyText"], fontSize=11.5, leading=17,
                               alignment=TA_JUSTIFY, spaceAfter=9),
        "bullet": ParagraphStyle("bullet", parent=ss["BodyText"], fontSize=11.5,
                                 leading=16.5, leftIndent=16, bulletIndent=4, spaceAfter=4),
        "caption": ParagraphStyle("caption", parent=ss["Normal"], fontSize=9.5, leading=13,
                                  textColor=MUTED, spaceAfter=12),
        "code": ParagraphStyle("code", parent=ss["Code"], fontSize=8.2, leading=10.5,
                               backColor=colors.HexColor("#0b1021"),
                               textColor=colors.HexColor("#e2e8f0"), borderPadding=7,
                               spaceBefore=6, spaceAfter=10),
    }


def _inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text


def _block_to_flowables(body: str, styles) -> list:
    flow = []
    for raw in body.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            flow.append(Paragraph(_inline(line.lstrip()[2:]), styles["bullet"],
                                  bulletText="\u2022"))
        elif re.match(r"^\d+\.\s", line.strip()):
            flow.append(Paragraph(_inline(line.strip()), styles["bullet"]))
        else:
            flow.append(Paragraph(_inline(line), styles["body"]))
    return flow


def _code_flowables(code: str, styles) -> list:
    lines = code.split("\n")
    flow = []
    chunk: list[str] = []
    for ln in lines:
        chunk.append(ln.replace("\t", "    "))
        if len(chunk) >= 42:
            flow.append(Preformatted("\n".join(chunk), styles["code"]))
            chunk = []
    if chunk:
        flow.append(Preformatted("\n".join(chunk), styles["code"]))
    return flow


def _on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2.3 * cm, 1.2 * cm, "AI-University Press")
    canvas.drawRightString(A4[0] - 2.3 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def render_pdf(book: Book, path: str) -> None:
    styles = _styles()
    doc = SimpleDocTemplate(
        path, pagesize=A4, topMargin=2.6 * cm, bottomMargin=2.2 * cm,
        leftMargin=2.6 * cm, rightMargin=2.6 * cm, title=book.title,
        author=", ".join(book.authors),
    )
    story: list = []

    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph(_inline(book.title), styles["title"]))
    story.append(Paragraph(_inline(book.subtitle), styles["subtitle"]))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f"{book.category} &nbsp;|&nbsp; Level: {book.level} &nbsp;|&nbsp; {book.edition}",
        styles["meta"]))
    story.append(Paragraph(f"Authors: {', '.join(book.authors)}", styles["meta"]))
    story.append(Paragraph(
        f"AI-University Press &nbsp;|&nbsp; ISBN {book.isbn} &nbsp;|&nbsp; v{book.version}",
        styles["meta"]))
    story.append(PageBreak())

    story.append(Paragraph("Copyright", styles["h1"]))
    story.append(Paragraph(
        f"Copyright &#169; {book.published} AI-University Press. All rights reserved.",
        styles["body"]))
    story.append(Paragraph(
        "This work is published as part of the AI-University Enterprise AI Knowledge "
        "Series and is generated by an automated publishing engine for professional and "
        "educational use.", styles["body"]))
    story.append(PageBreak())

    story.append(Paragraph("Table of Contents", styles["h1"]))
    for ch in book.chapters:
        story.append(Paragraph(f"{ch.number}. {escape(ch.title)} "
                               f"<font color='#94a3b8'>(~{ch.estimated_pages} pp.)</font>",
                               styles["body"]))
    story.append(PageBreak())

    fm = book.front_matter
    story.append(Paragraph("Learning Objectives", styles["h1"]))
    for o in fm.learning_objectives:
        story.append(Paragraph(_inline(o), styles["bullet"], bulletText="\u2022"))
    for heading, text in [
        ("Executive Summary", fm.executive_summary),
        ("Industry Context", fm.industry_context),
        ("Business Perspective", fm.business_perspective),
        ("Technical Perspective", fm.technical_perspective),
        ("Architecture Perspective", fm.architecture_perspective),
        ("Governance Perspective", fm.governance_perspective),
        ("Security Perspective", fm.security_perspective),
    ]:
        story.append(Paragraph(heading, styles["h1"]))
        story.extend(_block_to_flowables(text, styles))
    story.append(PageBreak())

    fig_no = 0
    for ch in book.chapters:
        story.append(Paragraph(f"Chapter {ch.number}. {escape(ch.title)}", styles["h1"]))
        story.append(Paragraph(_inline(ch.summary), styles["caption"]))
        for sec in ch.sections:
            story.append(Paragraph(escape(sec.heading), styles["h2"]))
            story.extend(_block_to_flowables(sec.body, styles))
            if sec.heading.startswith("Architecture"):
                for d in ch.diagrams:
                    fig_no += 1
                    story.append(Paragraph(
                        f"Figure {fig_no}. {escape(d.title)} ({d.fmt})", styles["h3"]))
                    story.extend(_code_flowables(d.source, styles))
                    story.append(Paragraph(_inline(d.caption), styles["caption"]))
        for cs in ch.code_samples:
            story.append(Paragraph(f"Listing: {escape(cs.title)}", styles["h3"]))
            story.extend(_code_flowables(cs.code, styles))
        story.append(Paragraph("Review Questions", styles["h2"]))
        for i, q in enumerate(ch.questions, 1):
            story.append(Paragraph(f"{i}. {_inline(q.question)}", styles["body"]))
            for j, opt in enumerate(q.options):
                story.append(Paragraph(f"{chr(ord('A')+j)}. {_inline(opt)}",
                                       styles["bullet"]))
            if q.answer_index >= 0:
                story.append(Paragraph(
                    f"<b>Answer: {chr(ord('A')+q.answer_index)}.</b> {_inline(q.explanation)}",
                    styles["body"]))
            else:
                story.append(Paragraph(f"<b>Guidance.</b> {_inline(q.explanation)}",
                                       styles["body"]))
        story.append(PageBreak())

    bm = book.back_matter
    story.append(Paragraph("Hands-On Labs", styles["h1"]))
    for lab in bm.labs:
        story.append(Paragraph(escape(lab["title"]), styles["h2"]))
        story.extend(_block_to_flowables(lab["body"], styles))
    story.append(Paragraph("Case Studies", styles["h1"]))
    for cs in bm.case_studies:
        story.append(Paragraph(escape(cs["title"]), styles["h2"]))
        story.extend(_block_to_flowables(cs["body"], styles))

    story.append(Paragraph("References", styles["h1"]))
    for i, r in enumerate(bm.references, 1):
        story.append(Paragraph(f"{i}. {escape(r)}", styles["body"]))

    story.append(Paragraph("Glossary", styles["h1"]))
    gdata = [["Term", "Definition"]] + [[g["term"], g["definition"]] for g in bm.glossary]
    gtable = Table(gdata, colWidths=[4.5 * cm, 10.5 * cm])
    gtable.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(gtable)

    story.append(Paragraph("Index", styles["h1"]))
    story.append(Paragraph(escape(", ".join(bm.index_terms)), styles["body"]))

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
