"""
+A utility script to format a full-length novel comprised of an introduction,
+25 chapters, and a conclusion. The script builds a consistent, professional
+layout with title pages, table of contents, and cleanly wrapped paragraphs.
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
+import pathlib
+import textwrap
+import re
+from typing import Iterable, List, Sequence
+
+
+LINE_WIDTH_DEFAULT = 84
+REQUIRED_CHAPTER_COUNT = 25
+
+
+def read_text(path: pathlib.Path) -> str:
+    """Read a UTF-8 text file and return its stripped contents."""
+    content = path.read_text(encoding="utf-8")
+    return content.strip()
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
+    return [read_text(path) for path in sorted_paths]
+
+
+def format_paragraphs(text: str, width: int) -> str:
+    """Wrap individual paragraphs to a fixed width while preserving breaks."""
+    paragraphs = [para.strip() for para in text.split("\n\n") if para.strip()]
+    wrapped = [textwrap.fill(para, width=width) for para in paragraphs]
+    return "\n\n".join(wrapped)
+
+
+def center_block(lines: Iterable[str], width: int) -> str:
+    """Return a centered multi-line block."""
+    centered = [line.strip().center(width) for line in lines]
+    return "\n".join(centered)
+
+
+def section_header(title: str, width: int, underline: str = "═") -> str:
+    """Create a distinct, padded section header."""
+    title_line = f" {title.strip()} ".center(width, underline)
+    return title_line
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
+def format_novel(
+    *,
+    title: str,
+    author: str,
+    intro_text: str,
+    chapters: Sequence[str],
+    conclusion_text: str,
+    tagline: str | None = None,
+    width: int = LINE_WIDTH_DEFAULT,
+) -> str:
+    """Combine all components into a polished Markdown-like document."""
+    formatted_sections: List[str] = []
+
+    # Title page
+    title_lines = [title]
+    if tagline:
+        title_lines.append(tagline)
+    title_lines.append(f"بقلم {author}")
+    title_page = "\n\n".join([
+        section_header("✦✦✦", width),
+        center_block(title_lines, width),
+        section_header("✦✦✦", width),
+    ])
+    formatted_sections.append(title_page)
+
+    # Table of contents
+    toc = build_table_of_contents("المقدمة", "الخاتمة", width)
+    formatted_sections.append(toc)
+
+    # Introduction
+    formatted_sections.append(section_header("المقدمة", width))
+    formatted_sections.append(format_paragraphs(intro_text, width))
+
+    # Chapters
+    for idx, chapter in enumerate(chapters, start=1):
+        formatted_sections.append(section_header(f"الفصل {idx}", width))
+        formatted_sections.append(format_paragraphs(chapter, width))
+
+    # Conclusion
+    formatted_sections.append(section_header("الخاتمة", width))
+    formatted_sections.append(format_paragraphs(conclusion_text, width))
+
+    # Decorative ending
+    formatted_sections.append(section_header("النهاية", width, underline="─"))
+    formatted_sections.append(center_block(["تمت"], width))
+
+    return "\n\n".join(formatted_sections) + "\n"
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
+    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("formatted_novel.md"))
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
+    intro_text = read_text(args.intro)
+    chapters = gather_chapters(chapter_paths)
+    conclusion_text = read_text(args.conclusion)
+
+    formatted = format_novel(
+        title=args.title,
+        author=args.author,
+        intro_text=intro_text,
+        chapters=chapters,
+        conclusion_text=conclusion_text,
+        tagline=args.tagline,
+        width=args.line_width,
+    )
+
+    args.output.write_text(formatted, encoding="utf-8")
+    print(f"تم إنشاء الملف المنسق: {args.output}")
+
+
+if __name__ == "__main__":
+    main()
