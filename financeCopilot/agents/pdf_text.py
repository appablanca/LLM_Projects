import fitz
import os

GIRDI_KLASORU = "girdi_klasoru"
CIKTI_KLASORU = "cikti_klasoru"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    return all_text

def get_first_txt_from_output_folder():
    txt_files = [f for f in os.listdir(CIKTI_KLASORU) if f.endswith(".txt")]
    if not txt_files:
        raise FileNotFoundError("cikti_klasoru içinde .txt dosyası yok.")
    first_txt_path = os.path.join(CIKTI_KLASORU, txt_files[0])
    with open(first_txt_path, "r", encoding="utf-8") as f:
        return f.read()
    
def main():
    if not os.path.exists(CIKTI_KLASORU):
        os.makedirs(CIKTI_KLASORU)

    for filename in os.listdir(GIRDI_KLASORU):
        filepath = os.path.join(GIRDI_KLASORU, filename)
        if os.path.isfile(filepath) and filepath.lower().endswith(".pdf"):
            print(f"İşleniyor (PDF): {filename}")
            text = extract_text_from_pdf(filepath)
            if text.strip():
                output_filename = os.path.splitext(filename)[0] + ".txt"
                output_path = os.path.join(CIKTI_KLASORU, output_filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Kaydedildi: {output_filename}")
            else:
                print(f"PDF boş veya metin çıkarılamadı: {filename}")
        else:
            print(f"Atlandı (PDF değil): {filename}")

if __name__ == "__main__":
    main()
