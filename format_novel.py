"""
+A utility script to format a full-length novel comprised of an introduction,
+25 chapters, and a conclusion. The script builds a consistent, professional
+layout with title pages, table of contents, and cleanly wrapped paragraphs.
+It can also export a right-to-left aware, print-ready PDF with embedded fonts
+and careful Arabic spacing.
+
+Usage examples:
+    python format_novel.py --title "Title" --author "Author" \
+        --intro intro.txt --chapters-dir chapters/ --conclusion outro.txt \
+        --output formatted_novel.md
+
+Alternatively, pass each chapter explicitly:
+    python format_novel.py --title "Title" --author "Author" \
+        --intro intro.txt \
+        --chapter c1.txt --chapter c2.txt ... --chapter c25.txt \
+        --conclusion outro.txt
+"""
+from __future__ import annotations
+
+import argparse
+import importlib
+import pathlib
+import re
+import textwrap
+from typing import Iterable, List, Sequence
+
+
+LINE_WIDTH_DEFAULT = 84
+PARAGRAPH_INDENT_DEFAULT = 0
+REQUIRED_CHAPTER_COUNT = 25
+ORNAMENT_DEFAULT = "✧"
+DEFAULT_PDF_FONT = "Amiri"
+
+
+def read_text(path: pathlib.Path) -> str:
+    """Read a UTF-8 text file and return its stripped contents."""
+    content = path.read_text(encoding="utf-8")
+    return content.lstrip("\ufeff").strip()
+
+
+def normalize_spacing(text: str) -> str:
+    """Normalize Arabic prose by collapsing noisy blank lines."""
+    # Replace multiple blank lines with a single, intentional break
+    text = re.sub(r"\n{3,}", "\n\n", text)
+    # Trim trailing whitespace on each line
+    return "\n".join(line.rstrip() for line in text.splitlines())
+
+
+def refine_arabic_punctuation(text: str) -> str:
+    """Apply light Arabic-aware punctuation cleanups for a polished feel."""
+    replacements = {
+        ",": "،",
+        "?": "؟",
+        ";": "؛",
+        "...": "…",
+        "\"": "”",
+        "'": "’",
+    }
+    refined = text
+    for raw, pretty in replacements.items():
+        refined = refined.replace(raw, pretty)
+    refined = re.sub(r"\s+([،؛؟…])", r"\1", refined)
+    return refined
+
+
+def ensure_not_empty(label: str, text: str) -> str:
+    """Ensure the provided text is not empty, raising a clear error otherwise."""
+    if not text.strip():
+        raise ValueError(f"المحتوى الخاص بـ {label} فارغ")
+    return refine_arabic_punctuation(normalize_spacing(text))
+
+
+def natural_sort_key(path: pathlib.Path) -> List:
+    """Return a key for human-friendly numeric sorting of file names.
+
+    The key is based on the stem of the file name (extension removed) and
+    splits any embedded digits so that "chapter2" sorts before "chapter10".
+    """
+
+    parts: List[str | int] = []
+    for chunk in re.split(r"(\d+)", path.stem):
+        if not chunk:
+            continue
+        parts.append(int(chunk) if chunk.isdigit() else chunk.lower())
+    return parts
+
+
+def gather_chapters(chapter_paths: Sequence[pathlib.Path]) -> List[str]:
+    """Read and validate chapter files.
+
+    The function ensures exactly 25 chapters are present and returns their
+    contents as a list ordered by file name.
+    """
+    sorted_paths = sorted(chapter_paths, key=natural_sort_key)
+    missing = [path for path in sorted_paths if not path.exists() or not path.is_file()]
+    if missing:
+        raise FileNotFoundError(
+            "أحد ملفات الفصول غير موجود أو ليس ملفًا صالحًا: "
+            + ", ".join(str(path) for path in missing)
+        )
+    if len(sorted_paths) != REQUIRED_CHAPTER_COUNT:
+        raise ValueError(
+            f"Expected {REQUIRED_CHAPTER_COUNT} chapters but received {len(sorted_paths)}"
+        )
+    return [ensure_not_empty(str(path), read_text(path)) for path in sorted_paths]
+
+
+def format_paragraphs(
+    text: str,
+    width: int,
+    indent: int = PARAGRAPH_INDENT_DEFAULT,
+    rtl_align: bool = False,
+    line_spacing: int = 1,
+) -> str:
+    """Wrap individual paragraphs with optional right alignment and spacing."""
+
+    paragraphs = [para.strip() for para in text.split("\n\n") if para.strip()]
+    indent_str = " " * max(indent, 0)
+    wrapped_blocks = []
+    for para in paragraphs:
+        wrapped = textwrap.fill(
+            para,
+            width=width,
+            initial_indent=indent_str,
+            subsequent_indent=indent_str,
+        ).splitlines()
+        if rtl_align:
+            wrapped = [line.rjust(width) for line in wrapped]
+        wrapped_blocks.append("\n".join(wrapped))
+
+    spacer = "\n" * max(line_spacing, 1)
+    return spacer.join(wrapped_blocks)
+
+
+def center_block(lines: Iterable[str], width: int) -> str:
+    """Return a centered multi-line block."""
+    centered = [line.strip().center(width) for line in lines]
+    return "\n".join(centered)
+
+
+def section_header(title: str, width: int, underline: str = "═", ornament: str = ORNAMENT_DEFAULT) -> str:
+    """Create a distinct, padded section header with subtle ornamentation."""
+    ornamented = f" {ornament} {title.strip()} {ornament} "
+    title_line = ornamented.center(width, underline)
+    return title_line
+
+
+def ornamental_break(width: int, symbol: str = ORNAMENT_DEFAULT) -> str:
+    """Return a centered ornamental break line."""
+    return center_block([symbol * 3], width)
+
+
+def split_paragraphs(text: str) -> List[str]:
+    """Split text into paragraphs while discarding empty segments."""
+
+    return [para.strip() for para in text.split("\n\n") if para.strip()]
+
+
+def word_count(text: str) -> int:
+    """Return a lightweight word count for a block of text."""
+    return len(re.findall(r"\S+", text))
+
+
+def build_statistics(
+    intro_text: str, chapters: Sequence[str], conclusion_text: str, width: int
+) -> str:
+    """Construct a centered statistics block summarizing word counts."""
+    lines = ["ملخص إحصائي", ""]
+    lines.append(f"كلمات المقدمة: {word_count(intro_text):,}")
+    for idx, chapter in enumerate(chapters, start=1):
+        lines.append(f"كلمات الفصل {idx}: {word_count(chapter):,}")
+    lines.append(f"كلمات الخاتمة: {word_count(conclusion_text):,}")
+    total_words = word_count(intro_text) + word_count(conclusion_text) + sum(
+        word_count(chapter) for chapter in chapters
+    )
+    lines.append("")
+    lines.append(f"إجمالي الكلمات: {total_words:,}")
+    return center_block(lines, width)
+
+
+def build_table_of_contents(intro_title: str, conclusion_title: str, width: int) -> str:
+    """Construct a simple table of contents with aligned numbering."""
+    lines = ["جدول المحتويات", "", f"1. {intro_title}"]
+    for idx in range(REQUIRED_CHAPTER_COUNT):
+        lines.append(f"{idx + 2}. الفصل {idx + 1}")
+    lines.append(f"{REQUIRED_CHAPTER_COUNT + 2}. {conclusion_title}")
+    return center_block(lines, width)
+
+
+def build_title_page(
+    *,
+    title: str,
+    author: str,
+    tagline: str | None,
+    epigraph: str | None,
+    width: int,
+    ornament: str,
+) -> str:
+    """Compose a lush title page with optional epigraph."""
+
+    title_lines = [title]
+    if tagline:
+        title_lines.append(tagline)
+    title_lines.append(f"بقلم {author}")
+
+    blocks = [
+        section_header("✦✦✦", width, ornament=ornament),
+        center_block(title_lines, width),
+        section_header("✦✦✦", width, ornament=ornament),
+    ]
+
+    if epigraph:
+        epigraph_block = "\n".join([
+            ornamental_break(width, ornament),
+            center_block([epigraph], width),
+            ornamental_break(width, ornament),
+        ])
+        blocks.append(epigraph_block)
+
+    return "\n\n".join(blocks)
+
+
+def ensure_module(module_name: str, friendly: str) -> object:
+    """Import and return a required module with a clear error if missing."""
+
+    spec = importlib.util.find_spec(module_name)
+    if spec is None:
+        raise ImportError(f"يتطلب التصدير إلى PDF وجود مكتبة {friendly} مثبتة")
+    module = importlib.import_module(module_name)
+    return module
+
+
+def shape_rtl_text(text: str) -> str:
+    """Return an RTL-shaped representation when bidi helpers are available."""
+
+    reshaper_spec = importlib.util.find_spec("arabic_reshaper")
+    bidi_spec = importlib.util.find_spec("bidi.algorithm")
+    if reshaper_spec and bidi_spec:
+        arabic_reshaper = importlib.import_module("arabic_reshaper")
+        bidi = importlib.import_module("bidi.algorithm")
+        return bidi.get_display(arabic_reshaper.reshape(text))
+    return text
+
+
+def format_novel(
+    *,
+    title: str,
+    author: str,
+    intro_text: str,
+    chapters: Sequence[str],
+    conclusion_text: str,
+    tagline: str | None = None,
+    width: int = LINE_WIDTH_DEFAULT,
+    paragraph_indent: int = PARAGRAPH_INDENT_DEFAULT,
+    include_stats: bool = False,
+    rtl_align: bool = False,
+    line_spacing: int = 1,
+    ornament: str = ORNAMENT_DEFAULT,
+    epigraph: str | None = None,
+) -> str:
+    """Combine all components into a polished Markdown-like document."""
+    formatted_sections: List[str] = []
+
+    # Title page
+    formatted_sections.append(
+        build_title_page(
+            title=title,
+            author=author,
+            tagline=tagline,
+            epigraph=epigraph,
+            width=width,
+            ornament=ornament,
+        )
+    )
+
+    # Table of contents
+    toc = build_table_of_contents("المقدمة", "الخاتمة", width)
+    formatted_sections.append(toc)
+
+    # Introduction
+    formatted_sections.append(section_header("المقدمة", width, ornament=ornament))
+    formatted_sections.append(
+        format_paragraphs(
+            intro_text,
+            width,
+            paragraph_indent,
+            rtl_align=rtl_align,
+            line_spacing=line_spacing,
+        )
+    )
+
+    if include_stats:
+        formatted_sections.append(build_statistics(intro_text, chapters, conclusion_text, width))
+
+    # Chapters
+    for idx, chapter in enumerate(chapters, start=1):
+        formatted_sections.append(section_header(f"الفصل {idx}", width, ornament=ornament))
+        formatted_sections.append(
+            format_paragraphs(
+                chapter,
+                width,
+                paragraph_indent,
+                rtl_align=rtl_align,
+                line_spacing=line_spacing,
+            )
+        )
+
+    # Conclusion
+    formatted_sections.append(section_header("الخاتمة", width, ornament=ornament))
+    formatted_sections.append(
+        format_paragraphs(
+            conclusion_text,
+            width,
+            paragraph_indent,
+            rtl_align=rtl_align,
+            line_spacing=line_spacing,
+        )
+    )
+
+    # Decorative ending
+    formatted_sections.append(section_header("النهاية", width, underline="─", ornament=ornament))
+    formatted_sections.append(center_block(["تمت"], width))
+
+    return "\n\n".join(formatted_sections) + "\n"
+
+
+def create_pdf(
+    *,
+    output_path: pathlib.Path,
+    title: str,
+    author: str,
+    tagline: str | None,
+    epigraph: str | None,
+    intro_text: str,
+    chapters: Sequence[str],
+    conclusion_text: str,
+    ornament: str,
+    page_size: str,
+    pdf_font: str,
+    paragraph_indent: int,
+    pdf_line_spacing: float,
+    header_spacing_before: float,
+    header_spacing_after: float,
+    chapter_page_break: bool,
+) -> None:
+    """Render the novel directly to a print-ready PDF."""
+
+    ensure_module("reportlab", "reportlab")
+    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
+    from reportlab.lib.pagesizes import A4, A5, A6
+    from reportlab.lib.styles import ParagraphStyle
+    from reportlab.lib.units import mm
+    from reportlab.pdfbase import pdfmetrics
+    from reportlab.pdfbase.ttfonts import TTFont
+    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
+
+    chosen_size = {"A4": A4, "A5": A5, "A6": A6}.get(page_size.upper(), A5)
+    side_margin = 15 * mm
+    vertical_margin = 22 * mm
+
+    font_path = pathlib.Path(pdf_font)
+    font_label = font_path.stem if font_path.suffix else pdf_font
+    registered = False
+    search_candidates = [font_path]
+    if not font_path.suffix:
+        search_candidates.append(pathlib.Path(__file__).with_name(f"{pdf_font}.ttf"))
+        search_candidates.append(pathlib.Path.cwd() / f"{pdf_font}.ttf")
+
+    for candidate in search_candidates:
+        if candidate.exists():
+            font_label = candidate.stem
+            pdfmetrics.registerFont(TTFont(font_label, str(candidate)))
+            registered = True
+            break
+
+    if not registered:
+        if font_label not in pdfmetrics.standardFonts and font_label not in pdfmetrics.getRegisteredFontNames():
+            font_label = "Helvetica"
+
+    doc = SimpleDocTemplate(
+        str(output_path),
+        pagesize=chosen_size,
+        rightMargin=side_margin,
+        leftMargin=side_margin,
+        topMargin=vertical_margin,
+        bottomMargin=vertical_margin,
+    )
+
+    base_font_size = 14
+    leading = base_font_size * pdf_line_spacing
+    para_style = ParagraphStyle(
+        name="ArabicBody",
+        fontName=font_label,
+        fontSize=base_font_size,
+        leading=leading,
+        alignment=TA_RIGHT,
+        rightIndent=2 * mm,
+        leftIndent=2 * mm,
+        firstLineIndent=paragraph_indent * base_font_size * 0.6,
+        wordWrap="RTL",
+        spaceAfter=base_font_size * max(pdf_line_spacing - 0.8, 0.3),
+    )
+
+    centered_style = ParagraphStyle(
+        name="ArabicCenter",
+        parent=para_style,
+        alignment=TA_CENTER,
+        firstLineIndent=0,
+    )
+
+    header_style = ParagraphStyle(
+        name="ArabicHeader",
+        parent=centered_style,
+        fontSize=base_font_size + 6,
+        leading=(base_font_size + 6) * pdf_line_spacing,
+        spaceBefore=header_spacing_before,
+        spaceAfter=header_spacing_after,
+    )
+
+    subheader_style = ParagraphStyle(
+        name="ArabicSubheader",
+        parent=centered_style,
+        fontSize=base_font_size + 2,
+        leading=(base_font_size + 2) * pdf_line_spacing,
+        spaceBefore=header_spacing_before / 2,
+        spaceAfter=header_spacing_after / 2,
+    )
+
+    ornament_style = ParagraphStyle(
+        name="ArabicOrnament",
+        parent=centered_style,
+        fontSize=base_font_size,
+        spaceBefore=base_font_size * 0.6,
+        spaceAfter=base_font_size * 0.6,
+    )
+
+    story = []
+
+    # Title page
+    story.append(Spacer(1, header_spacing_before))
+    story.append(Paragraph(shape_rtl_text(section_header("✦✦✦", 40, ornament=ornament)), ornament_style))
+    title_block = [title]
+    if tagline:
+        title_block.append(tagline)
+    title_block.append(f"بقلم {author}")
+    for line in title_block:
+        story.append(Paragraph(shape_rtl_text(line), header_style))
+    story.append(Paragraph(shape_rtl_text(section_header("✦✦✦", 40, ornament=ornament)), ornament_style))
+
+    if epigraph:
+        story.append(Spacer(1, base_font_size))
+        story.append(Paragraph(shape_rtl_text(ornament * 3), ornament_style))
+        story.append(Paragraph(shape_rtl_text(epigraph), centered_style))
+        story.append(Paragraph(shape_rtl_text(ornament * 3), ornament_style))
+
+    story.append(PageBreak())
+
+    # Table of contents
+    story.append(Paragraph(shape_rtl_text("جدول المحتويات"), header_style))
+    toc_lines = ["المقدمة"] + [f"الفصل {idx}" for idx in range(1, REQUIRED_CHAPTER_COUNT + 1)] + ["الخاتمة"]
+    for idx, label in enumerate(toc_lines, start=1):
+        story.append(Paragraph(shape_rtl_text(f"{idx}. {label}"), para_style))
+
+    story.append(PageBreak())
+
+    # Intro
+    story.append(Paragraph(shape_rtl_text(section_header("المقدمة", 40, ornament=ornament)), header_style))
+    for para in split_paragraphs(intro_text):
+        story.append(Paragraph(shape_rtl_text(para), para_style))
+    story.append(Paragraph(shape_rtl_text(ornament * 3), ornament_style))
+
+    # Chapters
+    for idx, chapter in enumerate(chapters, start=1):
+        if chapter_page_break:
+            story.append(PageBreak())
+        story.append(
+            Paragraph(
+                shape_rtl_text(section_header(f"الفصل {idx}", 40, ornament=ornament)),
+                header_style,
+            )
+        )
+        for para in split_paragraphs(chapter):
+            story.append(Paragraph(shape_rtl_text(para), para_style))
+        story.append(Paragraph(shape_rtl_text(ornament * 3), ornament_style))
+
+    # Conclusion
+    story.append(PageBreak())
+    story.append(Paragraph(shape_rtl_text(section_header("الخاتمة", 40, ornament=ornament)), header_style))
+    for para in split_paragraphs(conclusion_text):
+        story.append(Paragraph(shape_rtl_text(para), para_style))
+
+    story.append(Paragraph(shape_rtl_text(section_header("النهاية", 40, underline="─", ornament=ornament)), subheader_style))
+    story.append(Paragraph(shape_rtl_text("تمت"), centered_style))
+
+    doc.build(story)
+
+
+def parse_args() -> argparse.Namespace:
+    parser = argparse.ArgumentParser(description="تنسيق رواية مكوّنة من 25 فصلًا")
+    parser.add_argument("--title", required=True, help="عنوان الرواية")
+    parser.add_argument("--author", required=True, help="اسم المؤلف")
+    parser.add_argument("--intro", required=True, type=pathlib.Path, help="ملف المقدمة")
+    chapter_group = parser.add_mutually_exclusive_group(required=True)
+    chapter_group.add_argument(
+        "--chapters-dir",
+        type=pathlib.Path,
+        help="مجلد يحتوي على ملفات الفصول (25 ملفًا)",
+    )
+    chapter_group.add_argument(
+        "--chapter",
+        action="append",
+        type=pathlib.Path,
+        dest="chapters",
+        help="يمكن تمرير المسار لكل فصل (استخدم الخيار 25 مرة)",
+    )
+    parser.add_argument("--conclusion", required=True, type=pathlib.Path, help="ملف الخاتمة")
+    parser.add_argument("--tagline", help="جملة تعريفية قصيرة للرواية", default=None)
+    parser.add_argument(
+        "--line-width",
+        type=int,
+        default=LINE_WIDTH_DEFAULT,
+        help="عرض السطر الأقصى لتنسيق الفقرات",
+    )
+    parser.add_argument(
+        "--paragraph-indent",
+        type=int,
+        default=PARAGRAPH_INDENT_DEFAULT,
+        help="عدد المسافات التي تسبق كل فقرة لإضفاء مظهر احترافي",
+    )
+    parser.add_argument(
+        "--line-spacing",
+        type=int,
+        default=1,
+        help="عدد الأسطر الفارغة بين الفقرات لخلق إيقاع بصري هادئ",
+    )
+    parser.add_argument(
+        "--rtl-align",
+        action="store_true",
+        help="محاذاة الفقرات لليمين لإبراز الطابع العربي",
+    )
+    parser.add_argument(
+        "--ornament",
+        default=ORNAMENT_DEFAULT,
+        help="رمز زخرفي يحيط بالعناوين والفواصل",
+    )
+    parser.add_argument(
+        "--epigraph",
+        help="اقتباس افتتاحي قصير يهيئ أجواء الرواية",
+        default=None,
+    )
+    parser.add_argument(
+        "--include-stats",
+        action="store_true",
+        help="إضافة صفحة إحصائية توضح عدد كلمات كل جزء والفصول",
+    )
+    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("formatted_novel.md"))
+    parser.add_argument(
+        "--export-pdf",
+        action="store_true",
+        help="إخراج ملف PDF جاهز للطباعة بدلًا من Markdown",
+    )
+    parser.add_argument(
+        "--pdf-font",
+        default=DEFAULT_PDF_FONT,
+        help="اسم خط TTF أو مساره لتضمينه داخل ملف الـ PDF",
+    )
+    parser.add_argument(
+        "--page-size",
+        choices=["A4", "A5", "A6"],
+        default="A5",
+        help="حجم الصفحة لملف الـ PDF",
+    )
+    parser.add_argument(
+        "--pdf-line-spacing",
+        type=float,
+        default=1.6,
+        help="معامل تباعد الأسطر داخل PDF للحصول على قراءة مريحة",
+    )
+    parser.add_argument(
+        "--header-spacing-before",
+        type=float,
+        default=16.0,
+        help="مسافة (بوينت) قبل عناوين الفصول داخل PDF",
+    )
+    parser.add_argument(
+        "--header-spacing-after",
+        type=float,
+        default=12.0,
+        help="مسافة (بوينت) بعد عناوين الفصول داخل PDF",
+    )
+    parser.add_argument(
+        "--chapter-page-break",
+        action="store_true",
+        help="بدء كل فصل من صفحة جديدة داخل PDF",
+    )
+    parser.add_argument(
+        "--keep-markdown",
+        action="store_true",
+        help="الاحتفاظ بملف Markdown حتى عند تفعيل التصدير إلى PDF",
+    )
+    return parser.parse_args()
+
+
+def main() -> None:
+    args = parse_args()
+
+    if args.chapters_dir:
+        chapter_paths = [path for path in args.chapters_dir.iterdir() if path.is_file()]
+        if not chapter_paths:
+            raise ValueError("لم يتم العثور على ملفات في مجلد الفصول")
+    else:
+        chapter_paths = args.chapters or []
+
+    intro_text = ensure_not_empty("المقدمة", read_text(args.intro))
+    chapters = gather_chapters(chapter_paths)
+    conclusion_text = ensure_not_empty("الخاتمة", read_text(args.conclusion))
+
+    epigraph_text = refine_arabic_punctuation(args.epigraph) if args.epigraph else None
+
+    if not args.export_pdf or args.keep_markdown:
+        formatted = format_novel(
+            title=args.title,
+            author=args.author,
+            intro_text=intro_text,
+            chapters=chapters,
+            conclusion_text=conclusion_text,
+            tagline=args.tagline,
+            width=args.line_width,
+            paragraph_indent=args.paragraph_indent,
+            include_stats=args.include_stats,
+            rtl_align=args.rtl_align,
+            line_spacing=args.line_spacing,
+            ornament=args.ornament,
+            epigraph=epigraph_text,
+        )
+    else:
+        formatted = None
+
+    if args.export_pdf:
+        pdf_path = args.output if args.output.suffix.lower() == ".pdf" else args.output.with_suffix(".pdf")
+        create_pdf(
+            output_path=pdf_path,
+            title=args.title,
+            author=args.author,
+            tagline=args.tagline,
+            epigraph=epigraph_text,
+            intro_text=intro_text,
+            chapters=chapters,
+            conclusion_text=conclusion_text,
+            ornament=args.ornament,
+            page_size=args.page_size,
+            pdf_font=args.pdf_font,
+            paragraph_indent=args.paragraph_indent,
+            pdf_line_spacing=args.pdf_line_spacing,
+            header_spacing_before=args.header_spacing_before,
+            header_spacing_after=args.header_spacing_after,
+            chapter_page_break=args.chapter_page_break,
+        )
+        print(f"PDF successfully generated: {pdf_path}")
+        if not args.keep_markdown:
+            return
+
+    if formatted is not None:
+        md_path = args.output if args.output.suffix.lower() == ".md" else args.output.with_suffix(".md")
+        md_path.write_text(formatted, encoding="utf-8")
+        print(f"تم إنشاء الملف المنسق: {md_path}")
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)
