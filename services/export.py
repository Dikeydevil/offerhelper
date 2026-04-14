# services/export.py
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_docx_from_text(text: str, path: str) -> None:
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(path)


def build_pdf_from_text(text: str, path: str) -> None:
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    # простейшая верстка: строки сверху вниз
    x = 40
    y = height - 40
    for line in text.splitlines():
        if y < 40:  # новая страница, если ушли вниз
            c.showPage()
            y = height - 40
        c.drawString(x, y, line)
        y -= 14

    c.save()