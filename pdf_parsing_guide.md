# A Guide to Parsing PDFs for Local RAG Applications

This guide provides a comprehensive walkthrough for setting up a robust pipeline to parse both text-based and image-based (scanned) PDFs in Python. The solution is designed for offline use, making it ideal for local RAG (Retrieval-Augmented Generation) applications where data privacy and security are paramount.

This pipeline uses the `llmware` framework for high-level document management and the powerful `Tesseract` OCR engine for extracting text from images, with a focus on handling both English and Russian documents.

## Part 1: Environment Setup

A successful pipeline starts with a correctly configured environment. This solution requires a few system-level dependencies to handle PDF rendering and Optical Character Recognition (OCR).

### System Dependencies

#### 1. Tesseract OCR Engine

Tesseract is a powerful, open-source OCR engine that will perform the text extraction from images. You must install it on your system and, crucially, include the language packs for the languages you intend to process. For this guide, we need English and Russian.

**On Debian/Ubuntu:**
```bash
# Update your package list
sudo apt-get update

# Install Tesseract
sudo apt-get install -y tesseract-ocr

# Install the language packs for English and Russian
sudo apt-get install -y tesseract-ocr-eng tesseract-ocr-rus
```

**On macOS (using Homebrew):**
```bash
# Install Tesseract (this includes all language packs by default)
brew install tesseract
```

**On Windows:**
For Windows, official installers are not provided by the Tesseract project. The community-maintained fork from UB Mannheim is highly recommended.

1.  Download the installer from the [UB Mannheim Tesseract GitHub page](https://github.com/UB-Mannheim/tesseract/wiki). Look for an installer named something like `tesseract-ocr-w64-setup-v5.x.x.exe`.
2.  Run the installer.
3.  **Important:** During the installation process, you will be prompted to select components. Make sure to expand the "Language data" section and check the boxes for **"Russian"** and **"English"**.
4.  After installation, you must add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system's `Path` environment variable so that it can be called from the command line.

#### 2. Poppler

Poppler is a PDF rendering library that `llmware` uses under the hood to process PDF files, especially for extracting images.

**On Debian/Ubuntu:**
```bash
sudo apt-get install -y poppler-utils
```

**On macOS (using Homebrew):**
```bash
brew install poppler
```

**On Windows:**
Windows users will need to download the Poppler binaries and add them to their system's `Path`.

1.  Download the latest release from a trusted source. The [blog of another developer, oyyod](https://github.com/oyyod/poppler-windows/releases/), is a common recommendation.
2.  Extract the downloaded archive to a permanent location on your machine (e.g., `C:\poppler`).
3.  Add the `bin` subdirectory from your extracted folder (e.g., `C:\poppler\bin`) to your system's `Path` environment variable.

### Python Dependencies

With the system dependencies in place, the next step is to install the required Python libraries. These libraries provide the core functionality for the parsing pipeline. It is highly recommended to use a Python virtual environment to manage these dependencies.

```bash
# Install all required libraries in one command
pip install llmware pytesseract Pillow
```

-   **`llmware`**: This is the main framework that orchestrates the document processing. It handles creating a library, parsing documents, extracting text and images, and managing the underlying database.
-   **`pytesseract`**: This is the Python wrapper for the Tesseract OCR engine. We will use it to call Tesseract on the images extracted by `llmware`.
-   **`Pillow`**: This is a powerful image processing library that `pytesseract` uses to open and handle image files.

With both system and Python dependencies installed, the environment is now ready. The next part of this guide will cover the implementation of the parsing and OCR pipeline itself.

## Part 2: The Parsing and OCR Pipeline

This section provides the complete Python script that forms the core of our parsing pipeline. The script is designed to be run from the command line and will process all PDFs in a specified input folder, creating a structured JSON file for each.

### The Complete Script

Below is the full code for `run_parsing_pipeline.py`. Save this code in your project directory.

```python
import os
import json
from multiprocessing import Pool, cpu_count
from PIL import Image
import pytesseract
from llmware.library import Library
from llmware.configs import LLMWareConfig

# --- Configuration ---
# Path to the folder containing your PDF files
INPUT_PDFS_PATH = "path/to/your/pdfs"
# Path to the folder where JSON outputs will be saved
OUTPUT_JSON_PATH = "path/to/your/json_outputs"
# Name for the llmware library
LIBRARY_NAME = "pdf_parsing_library"
# Number of parallel processes to use
# We leave one CPU core free for other system tasks.
NUM_PROCESSES = max(1, cpu_count() - 1)


def process_single_pdf(pdf_path):
    """
    Processes a single PDF file:
    1. Parses the PDF with llmware to extract text and images.
    2. Performs OCR on extracted images using Tesseract.
    3. Combines the results into a structured JSON file.
    """
    try:
        print(f" > Processing: {os.path.basename(pdf_path)}")

        # Create a temporary library for each process to avoid conflicts
        # This is a robust pattern for multiprocessing with llmware
        process_lib_name = f"{LIBRARY_NAME}_{os.getpid()}"
        lib = Library().create_new_library(process_lib_name)

        # --- Step 1: Parse PDF with llmware ---
        # We add only one file. 'get_images=True' is crucial.
        lib.add_file(pdf_path, get_images=True)

        # Retrieve all parsed content (text and image blocks) for the document
        doc_id = lib.get_doc_id_by_filename(os.path.basename(pdf_path))
        if not doc_id:
            print(f"  - Error: Could not find doc_id for {os.path.basename(pdf_path)}")
            lib.delete_library(confirm_delete=True)
            return

        blocks = lib.get_all_document_blocks(doc_id)

        output_data = {
            "document_name": os.path.basename(pdf_path),
            "pages": []
        }

        page_content = {} # Dictionary to hold content for each page

        # --- Step 2: Process Text and Image Blocks ---
        for block in blocks:
            page_num = block.get("page_num", 0)
            if page_num not in page_content:
                page_content[page_num] = {"page_number": page_num, "text_blocks": []}

            if block.get("content_type") == "text":
                page_content[page_num]["text_blocks"].append({
                    "text": block.get("text_search", ""),
                    "bbox": block.get("geometry") # llmware provides some geometry data
                })

            elif block.get("content_type") == "image":
                img_filename = block.get("external_files")
                if img_filename:
                    image_path = os.path.join(lib.image_path, img_filename)

                    # --- Step 3: Perform OCR with Tesseract ---
                    try:
                        # Use pytesseract to get detailed OCR data, including coordinates
                        ocr_data = pytesseract.image_to_data(
                            Image.open(image_path),
                            lang='rus+eng',
                            output_type=pytesseract.Output.DICT
                        )

                        # Process the OCR data to group words into meaningful blocks
                        num_items = len(ocr_data['level'])
                        for i in range(num_items):
                            # We only care about actual words with some confidence
                            if int(ocr_data['conf'][i]) > 60 and ocr_data['text'][i].strip():
                                (x, y, w, h) = (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i])
                                page_content[page_num]["text_blocks"].append({
                                    "text": ocr_data['text'][i],
                                    "bbox": [x, y, x + w, y + h]
                                })

                    except Exception as ocr_error:
                        print(f"  - Warning: Could not perform OCR on {img_filename}. Reason: {ocr_error}")

        # --- Step 4: Save Structured JSON ---
        output_data["pages"] = sorted(page_content.values(), key=lambda p: p["page_number"])

        if not os.path.exists(OUTPUT_JSON_PATH):
            os.makedirs(OUTPUT_JSON_PATH)

        output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + ".json"
        output_filepath = os.path.join(OUTPUT_JSON_PATH, output_filename)

        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"  - Success: Saved JSON to {output_filepath}")

    except Exception as e:
        print(f"  - Error processing {os.path.basename(pdf_path)}: {e}")
    finally:
        # Clean up the temporary library for the process
        if 'lib' in locals():
            lib.delete_library(confirm_delete=True)


def main():
    """Main function to set up and run the parallel processing pool."""
    # Ensure input path exists
    if not os.path.isdir(INPUT_PDFS_PATH):
        print(f"Error: Input directory not found at '{INPUT_PDFS_PATH}'")
        print("Please update the INPUT_PDFS_PATH variable in the script.")
        return

    # Find all PDF files in the input directory
    pdf_files = [os.path.join(INPUT_PDFS_PATH, f) for f in os.listdir(INPUT_PDFS_PATH) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in '{INPUT_PDFS_PATH}'.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process.")
    print(f"Starting parallel processing with {NUM_PROCESSES} workers...")

    # Use a multiprocessing pool to process files in parallel
    with Pool(processes=NUM_PROCESSES) as pool:
        pool.map(process_single_pdf, pdf_files)

    print("\nProcessing complete.")


if __name__ == "__main__":
    main()
```

### How the Script Works

1.  **Configuration**: At the top of the script, you can easily configure the input/output paths and the number of processes to use.
2.  **Hybrid Approach**: The script uses `llmware` for what it excels at: parsing the complex PDF structure, extracting digital text, and isolating images. It then uses the specialized `pytesseract` library for fine-grained OCR control.
3.  **Multilingual OCR**: When calling `pytesseract`, the `lang='rus+eng'` parameter tells Tesseract to use both Russian and English language models, allowing it to accurately recognize text in both languages within the same document.
4.  **Structured JSON Output**: The script generates a JSON file for each PDF. This file contains the document's name and a list of its pages. Each page, in turn, contains a list of `text_blocks`, where each block has both the extracted `text` and its `bbox` (bounding box) coordinates on the page. This structured format is perfect for feeding into a RAG system, as it preserves spatial information.
5.  **Concurrency**: The entire process is wrapped in a multiprocessing pool. This allows the script to process multiple PDF documents in parallel, taking full advantage of the server's multiple CPU cores to significantly speed up the ingestion of large document collections.
6.  **Isolation and Cleanup**: Each parallel process creates its own temporary `llmware` library. This is a crucial design pattern that prevents conflicts and race conditions when multiple processes try to write to the same library database. These temporary libraries are automatically deleted after each file is processed, ensuring no unnecessary data is left behind.

## Part 3: Running the Pipeline

1.  **Save the script** as `run_parsing_pipeline.py`.
2.  **Update the configuration variables** at the top of the script:
    *   Set `INPUT_PDFS_PATH` to the full path of the folder containing your PDFs.
    *   Set `OUTPUT_JSON_PATH` to the folder where you want the final JSON files to be saved.
3.  **Run the script** from your terminal:
    ```bash
    python run_parsing_pipeline.py
    ```

The script will then process all the PDFs and generate the structured JSON outputs, ready for your RAG application.
