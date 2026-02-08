---
name: qmd-converter
description: Convert PDF/EPUB documents into multi-chapter Quarto book projects using Pixi. Use when the user asks to "Convert this PDF/EPUB to a Quarto book" or "Make a qmd book from this file".
---

# Quarto Book Converter

This skill converts PDF or EPUB files into a structured Quarto book project (specifically targeting the `mybook/` directory). It handles text extraction, chapter splitting, image management, and configuration updates.

## Workflow

1.  **Check Environment**:
    The script relies on `pymupdf`, `ebooklib`, `beautifulsoup4`, `pyyaml`, and `html2text`.
    **ALWAYS** check if these are installed in the current `pixi` environment before running the script.
    
    If you are unsure or if the user hasn't explicitly set up the environment, run:
    ```bash
    pixi add pymupdf ebooklib beautifulsoup4 pyyaml html2text
    ```

2.  **Execute Conversion**:
    Run the python conversion script. Assume the script is located at `scripts/convert_to_book.py` relative to this skill.
    
    ```bash
    pixi run python <path-to-skill>/scripts/convert_to_book.py <input_file_path> --output-dir mybook
    ```
    *(Replace `<input_file_path>` with the actual file path provided by the user)*

3.  **Verify Output**:
    - List files in `mybook/` to confirm `.qmd` chapters were created.
    - Check `mybook/images/` for extracted images.
    - Read `mybook/_quarto.yml` to confirm the `chapters` list was updated.

## Usage Guidelines

- **Input Files**: Ensure the user provides a valid path to a `.pdf` or `.epub` file.
- **Chapter Splitting**:
    - **EPUB**: Splits automatically based on internal structure.
    - **PDF**: Splits based on the Table of Contents (Outline). If no TOC exists, it creates a single large chapter.
- **Images**: Images are extracted to `mybook/images/` and referenced in the Markdown as `![](images/filename.ext)`. 
    - **Note for PDF**: To avoid redundancy in OCR-ed PDFs, full-page background images are skipped if significant text is extracted from the same page. Only "real" images (diagrams, photos, etc.) that do not cover the whole page or pages without a text layer are saved.

## Troubleshooting

- **"ModuleNotFoundError"**: Run the `pixi add ...` command listed in Step 1.
- **"No chapters generated"**: The PDF might be image-only (scanned) without OCR, or the EPUB structure is non-standard.