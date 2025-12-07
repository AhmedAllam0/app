
+This repository contains a single utility script `format_novel.py` that formats a
+full Arabic novel into a clean, professional layout.
 
+Key features
+- Builds a polished title page with optional tagline and author credit.
+- Generates a centered table of contents for an introduction, 25 chapters, and a conclusion.
+- Wraps paragraphs to a configurable line width while respecting blank lines.
+- Validates that exactly 25 chapter files are provided, either from a directory or explicit paths.
+- Optional paragraph indentation for a more professional look.
+- Optional statistics page summarizing word counts for the introduction, each chapter, and the conclusion.
+- Normalizes التشكيل والمسافات الفارغة ويهذب علامات الترقيم العربية تلقائيًا.
+- يدعم المحاذاة لليمين، مسافة الأسطر بين الفقرات، واختيار زخرفة مخصصة للعناوين.
+- يضيف اقتباسًا افتتاحيًا (Epigraph) لإضفاء مزاج خاص قبل الغوص في الفصول.
+
+Basic usage
+1. Prepare text files: introduction, 25 chapters, and a conclusion.
+2. Run the script, passing the relevant file paths:
+   python format_novel.py --title "عنوان" --author "اسم المؤلف" \
+       --intro intro.txt --chapters-dir chapters/ --conclusion outro.txt \
+       --tagline "جملة تعريفية" --paragraph-indent 2 --line-spacing 2 \
+       --rtl-align --ornament "❖" --epigraph "اقتباس قصير" \
+       --include-stats --output formatted_novel.md
+
+If you prefer explicit chapter files:
+   python format_novel.py --title "عنوان" --author "اسم المؤلف" \
+       --intro intro.txt --chapter c1.txt --chapter c2.txt ... --chapter c25.txt \
+       --conclusion outro.txt --rtl-align --ornament "✶" --output formatted_novel.md
+
+Print-ready PDF export
+- Add `--export-pdf` to produce a beautifully typeset Arabic PDF instead of Markdown.
+- Control the embedded font with `--pdf-font` (defaults to Amiri) and page size with
+  `--page-size A4|A5|A6` (default A5 paperback feel).
+- Adjust spacing with `--pdf-line-spacing`, `--header-spacing-before`, `--header-spacing-after`,
+  and force each chapter onto its own page via `--chapter-page-break`.
+- Keep the Markdown alongside the PDF by adding `--keep-markdown` if you need both outputs.
 
EOF
)
