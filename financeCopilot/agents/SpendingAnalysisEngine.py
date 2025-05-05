import os
import json
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

INPUT_FOLDER = "girdi_klasoru"
OUTPUT_FOLDER = "cikti_klasoru"

SUPPORTED_IMAGES = [".png", ".jpg", ".jpeg"]
SUPPORTED_PDFS = [".pdf"]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_pdf(file_path):
    data = {
        "source_file": os.path.basename(file_path),
        "type": "pdf",
        "pages": []
    }

    doc = fitz.open(file_path)
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        data["pages"].append({
            "page_number": page_num,
            "text": text
        })
    doc.close()
    return data

def process_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return {
        "source_file": os.path.basename(file_path),
        "type": "image",
        "text": text.strip()
    }

def main():
    for filename in os.listdir(INPUT_FOLDER):
        filepath = os.path.join(INPUT_FOLDER, filename)
        name, ext = os.path.splitext(filename.lower())

        try:
            if ext in SUPPORTED_PDFS:
                json_data = process_pdf(filepath)
            elif ext in SUPPORTED_IMAGES:
                json_data = process_image(filepath)
            else:
                print(f"Atlanıyor (desteklenmeyen format): {filename}")
                continue

            output_path = os.path.join(OUTPUT_FOLDER, f"{name}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

            print(f"İşlendi: {filename}")

        except Exception as e:
            print(f"Hata oluştu ({filename}): {e}")

if __name__ == "__main__":
    main()
