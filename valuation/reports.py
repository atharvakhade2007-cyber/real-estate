"""Valuation report generation (synchronous — no Celery).

Called directly inside the request cycle by the API views.
"""

import io
import logging

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .models import PredictionLog

logger = logging.getLogger(__name__)

NAVY = colors.HexColor("#0f172a")
SLATE = colors.HexColor("#334155")
EMERALD = colors.HexColor("#059669")
LIGHT = colors.HexColor("#f1f5f9")

BRAND = "PropVal AI"


def format_inr(value) -> str:
    """Indian digit grouping: 14500000 -> '1,45,00,000'."""
    value = int(round(float(value)))
    sign = "-" if value < 0 else ""
    digits = str(abs(value))
    if len(digits) <= 3:
        return f"{sign}{digits}"
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return f"{sign}{','.join(groups + [tail])}"


def format_compact(value) -> str:
    """14500000 -> '₹1.45 Cr', 8550000 -> '₹85.5 Lakhs'."""
    value = float(value)
    if value >= 1e7:
        return f"₹{value / 1e7:.2f} Cr"
    if value >= 1e5:
        return f"₹{value / 1e5:.2f} Lakhs"
    return f"₹{format_inr(value)}"


def monthly_emi(principal: float, annual_rate_pct: float, years: int) -> float:
    r = annual_rate_pct / 12 / 100
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "BrandTitle", parent=base["Title"], fontSize=24, textColor=NAVY, spaceAfter=2
        ),
        "subtitle": ParagraphStyle(
            "BrandSubtitle", parent=base["Normal"], fontSize=11, textColor=SLATE, alignment=TA_CENTER
        ),
        "heading": ParagraphStyle(
            "Section", parent=base["Heading2"], textColor=NAVY, spaceBefore=14, spaceAfter=6
        ),
        "note": ParagraphStyle(
            "Note", parent=base["Normal"], fontSize=8, textColor=SLATE, leading=11
        ),
    }


def build_report_pdf(log: PredictionLog) -> bytes:
    """Renders the branded valuation report to an in-memory PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, topMargin=18 * mm, bottomMargin=16 * mm,
        leftMargin=16 * mm, rightMargin=16 * mm, title=f"{BRAND} Valuation Report",
    )
    s = _styles()
    story = []

    header = Table(
        [[Paragraph(f'<font color="white">{BRAND}</font>', s["title"]),
          Paragraph('<font color="white">Property Valuation Report</font>', s["subtitle"])]],
        colWidths=[95 * mm, 83 * mm],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story += [header, Spacer(1, 8), HRFlowable(width="100%", color=EMERALD, thickness=2)]

    story.append(Paragraph("Property Parameters", s["heading"]))
    metro = f"{log.metro_distance_km:g} km" if log.metro_distance_km is not None else "—"
    params = [
        ["Locality", log.locality, "Total Area", f"{log.total_sqft:g} sq.ft"],
        ["Configuration", f"{log.bhk} BHK", "Bathrooms", str(log.bathrooms)],
        ["Furnishing", log.get_furnishing_display(), "Property Age", f"{log.property_age:g} yrs"],
        ["Parking", "Yes" if log.parking else "No", "Clubhouse", "Yes" if log.clubhouse else "No"],
        ["Metro Distance", metro, "Generated On", log.created_at.strftime("%d %b %Y, %H:%M")],
    ]
    t = Table(params, colWidths=[35 * mm, 53 * mm, 40 * mm, 50 * mm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [t]

    story.append(Paragraph("Valuation Summary", s["heading"]))
    summary = [
        ["Estimated Valuation", f"₹{format_inr(log.predicted_price)}  ({format_compact(log.predicted_price)})"],
        ["Price per Sq.Ft", f"₹{format_inr(log.price_per_sqft)}"],
        ["Confidence Range (±4%)", f"₹{format_inr(log.range_low)} — ₹{format_inr(log.range_high)}"],
        ["Model", "XGBoost regression pipeline" if log.model_used == "xgboost" else "Heuristic estimate (dev)"],
    ]
    t = Table(summary, colWidths=[55 * mm, 123 * mm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TEXTCOLOR", (1, 0), (1, 0), EMERALD),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
    ]))
    story += [t]

    story.append(Paragraph("EMI Estimation (8.5% p.a.interest, 20% down payment)", s["heading"]))
    loan = float(log.predicted_price) * 0.80
    emi_rows = [["Loan Tenure", "Monthly EMI", "Total Interest", "Total Payable"]]
    for years in (10, 15, 20, 25, 30):
        emi_val = monthly_emi(loan, 8.5, years)
        total = emi_val * years * 12
        emi_rows.append([
            f"{years} years",
            f"₹{format_inr(emi_val)}",
            f"₹{format_inr(total - loan)}",
            f"₹{format_inr(total)}",
        ])
    t = Table(emi_rows, colWidths=[35 * mm, 44 * mm, 48 * mm, 51 * mm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]))
    story += [t, Spacer(1, 14), HRFlowable(width="100%", color=colors.HexColor("#cbd5e1"), thickness=0.6)]

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"This valuation is an algorithmic estimate generated by {BRAND} and is for "
        "informational purposes only. It should not be treated as a formal appraisal. "
        "Actual market prices may vary based on condition, floor, view, negotiation and "
        "market movement. EMI figures assume a fixed interest rate over the full tenure.",
        s["note"],
    ))

    doc.build(story)
    return buffer.getvalue()


def ensure_report_file(log: PredictionLog) -> None:
    """Generates and attaches the PDF to the log if not already present."""
    if log.report:
        return
    pdf_bytes = build_report_pdf(log)
    log.report.save(f"propval-valuation-{log.pk}.pdf", ContentFile(pdf_bytes), save=True)


def send_report_email(log: PredictionLog, recipient_email: str) -> None:
    """Builds (if needed) and emails the valuation report."""
    ensure_report_file(log)

    price_display = format_compact(log.predicted_price)
    message = EmailMessage(
        subject=f"Your {BRAND} valuation report — {log.locality} ({price_display})",
        body=(
            f"Hello,\n\n"
            f"Thank you for using {BRAND}.\n\n"
            f"Your valuation for {log.bhk} BHK in {log.locality} "
            f"({log.total_sqft:g} sq.ft) is attached.\n\n"
            f"Estimated value: {price_display}\n"
            f"Price per sq.ft: ₹{format_inr(log.price_per_sqft)}\n\n"
            f"— The {BRAND} Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    with log.report.open("rb") as fh:
        message.attach(log.report.name.rsplit("/", 1)[-1], fh.read(), "application/pdf")
    message.send(fail_silently=False)

    log.emailed_to = recipient_email
    log.save(update_fields=["emailed_to"])
    logger.info("Valuation report for prediction %s emailed to %s", log.pk, recipient_email)
