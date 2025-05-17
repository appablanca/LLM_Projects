import fitz  # PyMuPDF
import os

OUTPUT_FOLDER = "cikti_klasoru"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    return all_text

def process_pdf(pdf_path):
    messages = []

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    if os.path.isfile(pdf_path) and pdf_path.lower().endswith(".pdf"):
        filename = os.path.basename(pdf_path)
        messages.append(f"Processing (PDF): {filename}")
        text = extract_text_from_pdf(pdf_path)
        if text.strip():
            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            messages.append(f"Saved: {output_filename}")
        else:
            messages.append(f"PDF is empty or text could not be extracted: {filename}")
    else:
        messages.append(f"Skipped (Not a PDF): {pdf_path}")

    return messages

# Example usage
if __name__ == "__main__":
    pdf_file = "dosya.pdf"  # burada işlemek istediğin PDF dosyasının yolunu belirt
    results = process_pdf(pdf_file)
    for line in results:
        print(line)
