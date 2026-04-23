import io
import json
import base64
import os
from datetime import date
# USE reportlab to make pdfs

from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser 
from dotenv import load_dotenv 

from reportlab.lib.pagesizes import letter 
from reportlab.lib.units import inch 
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

load_dotenv()

# Get the Colors for the pdf doc
PRIMARY_DARK = HexColor("#1f2937")
ACCENT_ORANGE = HexColor("#f97316")
TEXT_DARK = HexColor("#111827")
TEXT_MUTED = HexColor("#6b7280")
RULE_COLOR = HexColor("#e5e7eb")
STAT_BG = HexColor("#f9fafb")

# Setup the Prompt for it generate the report
REPORT_PROMPT = """You are a professional basketball analytics writer for EliteBK.
You will receive a user question, an existing answer, and supporting source snippets.
Expand the answer into a structured in-depth analytical report.

Return ONLY a valid JSON object with exactly these keys:
{{
  "overview": "<2-3 paragraphs of narrative context>",
  "key_statistics": [
    {{"label": "<stat name>", "value": "<numeric or string value>", "context": "<1 sentence of significance>"}}
  ],
  "detailed_analysis": "<3-5 paragraphs of deep analysis>",
  "context_and_comparisons": "<2-3 paragraphs comparing to historical data, peers, or league averages>",
  "conclusion": "<1-2 paragraphs wrapping up the significance>"
}}

Rules:
- Use ONLY information present in the original answer and sources. Do not fabricate statistics.
- key_statistics must contain between 3 and 8 entries.
- All string values must be plain text — no markdown, no bullet characters.
- Return nothing outside the JSON object — no preamble, no code fences.

ORIGINAL QUESTION:
{question}

EXISTING ANSWER:
{answer}

SOURCE SNIPPETS:
{sources}"""

# function to get the gemini model
def get_llm():
    # just follow the one in rag_service
    chat_model = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.1-flash-lite-preview")
    return ChatGoogleGenerativeAI(
        model=chat_model,
        temperature=0.3,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )


def generate_report_content(question: str, answer: str, sources: list) -> dict:
    # use the sources
    formatted_sources = "\n---\n".join(
        s.get("snippet", "") for s in sources if s.get("snippet")
    ) or "No sources provided."

    # use the template to invoke
    prompt_template = ChatPromptTemplate.from_template(REPORT_PROMPT)
    chain = prompt_template | get_llm() | StrOutputParser()
    raw = chain.invoke({"question": question, "answer": answer, "sources": formatted_sources})

    #stripping for JSON files
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nRaw output: {raw[:300]}")

    # Normalize key_statistics entries so missing keys don't crash the PDF builder
    stats = data.get("key_statistics", [])
    normalized = []
    for s in stats:
        normalized.append({
            "label": s.get("label", ""),
            "value": s.get("value", ""),
            "context": s.get("context", ""),
        })
    data["key_statistics"] = normalized
    return data


# found dfunction to make footer
def _draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawCentredString(
        letter[0] / 2,
        0.5 * inch,
        "EliteBK — Analytics Report",
    )
    canvas.drawRightString(
        letter[0] - 0.75 * inch,
        0.5 * inch,
        f"Page {doc.page}",
    )
    canvas.restoreState()


# Function to actualy build pdf
def build_pdf(report_data: dict, question: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.9 * inch,
    )
    # set width
    usable_width = letter[0] - 1.5 * inch

    # Set all the style shere
    normal_style = ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=6,
    )
    section_label_style = ParagraphStyle(
        "SectionLabel",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=PRIMARY_DARK,
        spaceBefore=14,
        spaceAfter=6,
    )
    question_style = ParagraphStyle(
        "Question",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=TEXT_DARK,
        spaceBefore=10,
        spaceAfter=8,
        leading=18,
    )

    story = []

    # ── Header table ──────────────────────────────────────────────────────────
    today = date.today().strftime("%B %d, %Y")
    header_data = [[
        Paragraph('<font color="white" size="18"><b>EliteBK Analytics Report</b></font>', normal_style),
        Paragraph(f'<font color="white" size="9">{today}</font>', ParagraphStyle(
            "DateRight", fontName="Helvetica", fontSize=9, textColor=white, alignment=TA_RIGHT
        )),
    ]]
    header_table = Table(header_data, colWidths=[usable_width * 0.72, usable_width * 0.28])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_DARK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (0, -1), 12),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 12),
    ]))
    story.append(header_table)

    # Questions
    story.append(Paragraph(question, question_style))
    story.append(HRFlowable(width="100%", thickness=1, color=RULE_COLOR, spaceAfter=8))

    def add_section(label: str, text: str):
        story.append(Paragraph(label, section_label_style))
        for para in text.split("\n"):
            para = para.strip()
            if para:
                story.append(Paragraph(para, normal_style))

    # Overview sec
    add_section("Overview", report_data.get("overview", ""))

    # Stats section
    stats = report_data.get("key_statistics", [])
    if stats:
        story.append(Paragraph("Key Statistics", section_label_style))
        label_style = ParagraphStyle("StatLabel", fontName="Helvetica-Bold", fontSize=9, textColor=TEXT_DARK)
        value_style = ParagraphStyle("StatValue", fontName="Helvetica-Bold", fontSize=11, textColor=ACCENT_ORANGE)
        ctx_style = ParagraphStyle("StatCtx", fontName="Helvetica", fontSize=9, textColor=TEXT_MUTED)

        stat_rows = [["Label", "Value", "Context"]]  # header row
        for s in stats:
            stat_rows.append([
                Paragraph(s["label"], label_style), 
                Paragraph(s["value"], value_style),
                Paragraph(s["context"], ctx_style),
            ])

        col_widths = [usable_width * 0.28, usable_width * 0.18, usable_width * 0.54]
        stat_table = Table(stat_rows, colWidths=col_widths, repeatRows=1)

        row_count = len(stat_rows)
        table_styles = [
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, RULE_COLOR),
        ]
        for i in range(1, row_count):
            bg = STAT_BG if i % 2 == 1 else white
            table_styles.append(("BACKGROUND", (0, i), (-1, i), bg))
        stat_table.setStyle(TableStyle(table_styles))
        story.append(stat_table)

    #remaining sections
    add_section("Detailed Analysis", report_data.get("detailed_analysis", ""))
    add_section("Context & Comparisons", report_data.get("context_and_comparisons", ""))
    add_section("Conclusion", report_data.get("conclusion", ""))

    doc.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    return buffer.getvalue()


def encode_pdf(pdf_bytes: bytes) -> str:
    return base64.b64encode(pdf_bytes).decode("utf-8")
