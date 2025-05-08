import fitz  # PyMuPDF
import os

INPUT_FOLDER = "girdi_klasoru"
OUTPUT_FOLDER = "cikti_klasoru"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    return all_text

def process_pdfs():
    messages = []

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    for filename in os.listdir(INPUT_FOLDER):
        filepath = os.path.join(INPUT_FOLDER, filename)
        if os.path.isfile(filepath) and filepath.lower().endswith(".pdf"):
            messages.append(f"Processing (PDF): {filename}")
            text = extract_text_from_pdf(filepath)
            if text.strip():
                output_filename = os.path.splitext(filename)[0] + ".txt"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                messages.append(f"Saved: {output_filename}")
            else:
                messages.append(f"PDF is empty or text could not be extracted: {filename}")
        else:
            messages.append(f"Skipped (Not a PDF): {filename}")

    return messages

# Example usage
if __name__ == "__main__":
    results = process_pdfs()
    for line in results:
        print(line)