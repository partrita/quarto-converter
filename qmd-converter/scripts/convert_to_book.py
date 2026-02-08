import os
import sys
import argparse
import yaml
import shutil
from pathlib import Path

# Imports inside try-except blocks to allow the script to run/fail gracefully
# if dependencies aren't installed yet (handled by SKILL.md instructions)
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    epub = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import html2text
except ImportError:
    html2text = None

def error_exit(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)

def ensure_dependencies():
    missing = []
    if fitz is None: missing.append("pymupdf")
    if epub is None: missing.append("ebooklib")
    if BeautifulSoup is None: missing.append("beautifulsoup4")
    if html2text is None: missing.append("html2text")
    if 'yaml' not in sys.modules: missing.append("pyyaml")
    
    if missing:
        error_exit(f"Missing dependencies: {', '.join(missing)}. Please install them using 'pixi add {' '.join(missing)}'.")

def get_unique_filename(directory, base_name, ext):
    counter = 1
    filename = f"{base_name}{ext}"
    while (directory / filename).exists():
        filename = f"{base_name}_{counter}{ext}"
        counter += 1
    return filename

def clean_text_for_markdown(text):
    # Basic cleanup
    if not text:
        return ""
    return text.strip()

def process_epub(file_path, output_dir, images_dir):
    print(f"Processing EPUB: {file_path}")
    book = epub.read_epub(file_path)
    
    chapters = []
    image_map = {} # Map internal image names to new paths

    # 1. Extract Images
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_IMAGE:
            img_data = item.get_content()
            ext = Path(item.get_name()).suffix
            if not ext: ext = ".jpg" # Default
            
            new_img_name = get_unique_filename(images_dir, "img", ext)
            new_img_path = images_dir / new_img_name
            
            with open(new_img_path, "wb") as f:
                f.write(img_data)
            
            image_map[item.get_name()] = f"images/{new_img_name}"

    # 2. Extract Chapters
    # Using spine to get reading order
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0 # No wrapping
    
    chapter_count = 0
    
    for item_id in book.spine:
        item = book.get_item_with_id(item_id[0])
        if not item: continue
        
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            
            # Fix image sources
            for img in soup.find_all('img'):
                src = img.get('src')
                # Try to find the image in our map. EPUB paths can be tricky.
                # Simple heuristic: match filename
                if src:
                    src_name = Path(src).name
                    # Find matching key in image_map (keys are full internal paths)
                    for key, val in image_map.items():
                        if Path(key).name == src_name:
                            img['src'] = val
                            break
            
            # Extract Text/Markdown
            # Get title if possible
            title_tag = soup.find(['h1', 'h2', 'h3'])
            title = title_tag.get_text() if title_tag else f"Chapter {chapter_count + 1}"
            
            md_content = h.handle(str(soup))
            
            if len(md_content.strip()) < 50: # Skip empty/tiny chapters
                continue

            chapter_count += 1
            chapter_filename = f"chapter_{chapter_count:02d}.qmd"
            chapter_path = output_dir / chapter_filename
            
            with open(chapter_path, "w") as f:
                f.write(f"# {title}

")
                f.write(md_content)
            
            chapters.append(chapter_filename)
            print(f"Generated {chapter_filename}: {title}")

    return chapters

def process_pdf(file_path, output_dir, images_dir):
    print(f"Processing PDF: {file_path}")
    doc = fitz.open(file_path)
    toc = doc.get_toc()
    
    chapters = []
    
    # If no TOC, treat as one big chapter (or split by fixed pages? Let's do one big for now to be safe)
    if not toc:
        print("No Table of Contents found in PDF. Converting as single chapter.")
        toc = [[1, "Full Document", 1]] # level, title, page_num

    # Add a dummy end entry for loop logic
    toc.append([1, "End", doc.page_count + 1])

    for i in range(len(toc) - 1):
        level, title, start_page = toc[i]
        _, _, end_page = toc[i+1] # Look ahead for end page
        
        # PyMuPDF pages are 0-indexed, TOC is usually 1-indexed
        start_idx = start_page - 1
        end_idx = end_page - 1
        
        if start_idx >= doc.page_count: break
        
        chapter_md = ""
        
        # Iterate pages in this chapter
        for p_idx in range(start_idx, min(end_idx, doc.page_count)):
            page = doc[p_idx]
            
            # Extract Text
            text = page.get_text()
            chapter_md += text + "

"
            
            # Extract Images
            image_list = page.get_images(full=True)
            for img_info in image_list:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                img_name = get_unique_filename(images_dir, f"pdf_p{p_idx+1}_img", f".{image_ext}")
                img_path = images_dir / img_name
                
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                # Insert reference into markdown (approximate location is hard in plain text extraction, appending to bottom of page text is safe default)
                chapter_md += f"

![](images/{img_name})

"

        chapter_filename = f"chapter_{i+1:02d}.qmd"
        chapter_path = output_dir / chapter_filename
        
        with open(chapter_path, "w") as f:
            f.write(f"# {title}

")
            f.write(chapter_md)
            
        chapters.append(chapter_filename)
        print(f"Generated {chapter_filename}: {title}")

    return chapters

def update_quarto_yml(yml_path, new_chapters):
    if not yml_path.exists():
        print(f"Warning: {yml_path} not found. Creating basic config.")
        config = {"project": {"type": "book"}, "book": {"title": "Converted Book", "chapters": []}}
    else:
        with open(yml_path, 'r') as f:
            config = yaml.safe_load(f) or {}

    if "book" not in config:
        config["book"] = {}
    
    if "chapters" not in config["book"]:
        config["book"]["chapters"] = []
        
    # Append new chapters if not already present
    existing_chapters = set(config["book"]["chapters"])
    for ch in new_chapters:
        if ch not in existing_chapters:
            config["book"]["chapters"].append(ch)
            
    with open(yml_path, 'w') as f:
        yaml.dump(config, f, sort_keys=False)
    
    print(f"Updated {yml_path} with {len(new_chapters)} new chapters.")

def main():
    parser = argparse.ArgumentParser(description="Convert PDF/EPUB to Quarto Book")
    parser.add_argument("input_file", help="Path to input PDF or EPUB")
    parser.add_argument("--output-dir", default="mybook", help="Target Quarto project directory")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    output_path = Path(args.output_dir)
    images_path = output_path / "images"
    
    if not input_path.exists():
        error_exit(f"Input file not found: {input_path}")
        
    ensure_dependencies()
    
    # Create directories
    output_path.mkdir(parents=True, exist_ok=True)
    images_path.mkdir(parents=True, exist_ok=True)
    
    # Process
    ext = input_path.suffix.lower()
    if ext == ".epub":
        chapters = process_epub(input_path, output_path, images_path)
    elif ext == ".pdf":
        chapters = process_pdf(input_path, output_path, images_path)
    else:
        error_exit(f"Unsupported file format: {ext}. Only .pdf and .epub are supported.")
        
    if chapters:
        update_quarto_yml(output_path / "_quarto.yml", chapters)
        print("Conversion Complete!")
    else:
        print("No chapters were generated.")

if __name__ == "__main__":
    main()
