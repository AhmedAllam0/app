
+This repository contains a single utility script `format_novel.py` that formats a
+full Arabic novel into a clean, professional layout.
 
+Key features
+- Builds a polished title page with optional tagline and author credit.
+- Generates a centered table of contents for an introduction, 25 chapters, and a conclusion.
+- Wraps paragraphs to a configurable line width while respecting blank lines.
+- Validates that exactly 25 chapter files are provided, either from a directory or explicit paths.
+
+Basic usage
+1. Prepare text files: introduction, 25 chapters, and a conclusion.
+2. Run the script, passing the relevant file paths:
+   python format_novel.py --title "عنوان" --author "اسم المؤلف" \
+       --intro intro.txt --chapters-dir chapters/ --conclusion outro.txt \
+       --tagline "جملة تعريفية" --output formatted_novel.md
+
+If you prefer explicit chapter files:
+   python format_novel.py --title "عنوان" --author "اسم المؤلف" \
+       --intro intro.txt --chapter c1.txt --chapter c2.txt ... --chapter c25.txt \
+       --conclusion outro.txt --output formatted_novel.md
 
EOF
)
