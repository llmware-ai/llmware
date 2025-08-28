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


def setup_library():
    """Initializes llmware configuration and creates a new library."""
    print(" > Setting up llmware...")
    # Use local file-based databases for easy setup
    LLMWareConfig().set_active_db("sqlite")
    LLMWareConfig().set_vector_db("chromadb")

    # Create a new library, which will also create the necessary folder structure
    lib = Library().create_new_library(LIBRARY_NAME)
    return lib

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
                # For text blocks, we can approximate the bounding box if needed,
                # or use the text directly. For simplicity, we'll just add the text.
                # llmware's enterprise version provides exact coordinates.
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
