"""
Формирование оформленного .docx файла со сводкой звонка — для скачивания
из модального окна сводки на фронте.
"""

import io
from datetime import datetime

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

ACCENT_COLOR = RGBColor(0x2F, 0x54, 0x96)  # тёмно-синий акцент
MUTED_COLOR = RGBColor(0x5A, 0x5A, 0x5A)

SECTIONS = (
    ("discussion", "О чём говорили"),
    ("agreements", "Договорённости"),
    ("risks", "Риски / потерянные сделки"),
)


def _format_duration(total_seconds: int) -> str:
    minutes, seconds = divmod(int(total_seconds or 0), 60)
    return f"{minutes} мин {seconds:02d} сек"


def _shade_cell(cell, hex_color: str) -> None:
    """Заливка ячейки таблицы (без использования w:val='clear' -> ShadingType.CLEAR аналог)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.makeelement(qn("w:shd"), {
        qn("w:val"): "clear",
        qn("w:color"): "auto",
        qn("w:fill"): hex_color,
    })
    tc_pr.append(shd)


def _add_info_table(document: Document, rows: list[tuple[str, str]]) -> None:
    table = document.add_table(rows=len(rows), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False

    label_width = Cm(4.5)
    value_width = Cm(11.5)

    for row_idx, (label, value) in enumerate(rows):
        label_cell = table.rows[row_idx].cells[0]
        value_cell = table.rows[row_idx].cells[1]

        label_cell.width = label_width
        value_cell.width = value_width
        _shade_cell(label_cell, "F0F2F8")

        label_run = label_cell.paragraphs[0].add_run(label)
        label_run.bold = True
        label_run.font.size = Pt(10.5)
        label_run.font.color.rgb = MUTED_COLOR

        value_run = value_cell.paragraphs[0].add_run(value)
        value_run.font.size = Pt(10.5)


def _add_section(document: Document, title: str, value: str, examples: list[str]) -> None:
    heading = document.add_heading(level=2)
    run = heading.add_run(title)
    run.font.color.rgb = ACCENT_COLOR

    value_title = document.add_paragraph()
    value_title_run = value_title.add_run("Вывод")
    value_title_run.bold = True
    value_title_run.font.size = Pt(10.5)
    value_title_run.font.color.rgb = MUTED_COLOR

    for line in (value or "—").split("\n"):
        if line.strip():
            document.add_paragraph(line.strip())

    if examples:
        examples_title = document.add_paragraph()
        examples_title_run = examples_title.add_run("Примеры из разговора")
        examples_title_run.bold = True
        examples_title_run.font.size = Pt(10.5)
        examples_title_run.font.color.rgb = MUTED_COLOR

        for example_text in examples:
            p = document.add_paragraph(style="List Bullet")
            run = p.add_run(f"«{example_text.strip()}»")
            run.italic = True

    document.add_paragraph()  # отступ между секциями


def build_summary_docx(
    manager_full_name: str,
    organization: str,
    call_datetime: datetime,
    duration_seconds: int,
    summary: dict,
) -> bytes:
    """
    summary — словарь вида:
    {
      "discussion": {"value": "...", "examples": ["...", ...]},
      "agreements": {"value": "...", "examples": [...]},
      "risks": {"value": "...", "examples": [...]},
    }
    Возвращает содержимое .docx файла в виде байтов.
    """
    document = Document()

    section = document.sections[0]
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)

    title = document.add_heading(level=0)
    title_run = title.add_run("Сводка телефонного звонка")
    title_run.font.color.rgb = ACCENT_COLOR
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT

    document.add_paragraph()

    _add_info_table(document, [
        ("Дата и время", call_datetime.strftime("%d.%m.%Y %H:%M")),
        ("Менеджер", manager_full_name),
        ("Организация", organization),
        ("Продолжительность", _format_duration(duration_seconds)),
    ])

    document.add_paragraph()

    for key, title_text in SECTIONS:
        category = summary.get(key, {}) or {}
        _add_section(
            document,
            title_text,
            category.get("value", ""),
            category.get("examples", []) or [],
        )

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.read()