from PIL import Image
import pytesseract
import os

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

#tesseract windows için indirmek gerek:
#The latest installers can be downloaded here: tesseract-ocr-w64-setup-5.5.0.20241111.exe (64 bit)
#indiririken ekstra dil paketlerini de indirip kurmak gerek !!

GIRDI_KLASORU = "girdi_klasoru"
CIKTI_KLASORU = "cikti_klasoru"

DESTEKLENEN_UZANTILAR = [".jpg", ".jpeg", ".png"]

gorsel_dosyasi = None
for dosya in os.listdir(GIRDI_KLASORU):
    if os.path.splitext(dosya)[1].lower() in DESTEKLENEN_UZANTILAR:
        gorsel_dosyasi = dosya
        break

if not gorsel_dosyasi:
    print("Error: girdi_klasoru içinde uygun bir görsel bulunamadı.")
else:
    image_path = os.path.join(GIRDI_KLASORU, gorsel_dosyasi)
    print(f"Image Found: {image_path}")

    try:
        image = Image.open(image_path)

        text = pytesseract.image_to_string(image, lang="tur")

        if not os.path.exists(CIKTI_KLASORU):
            os.makedirs(CIKTI_KLASORU)

        txt_adi = os.path.splitext(gorsel_dosyasi)[0] + ".txt"
        txt_yolu = os.path.join(CIKTI_KLASORU, txt_adi)

        with open(txt_yolu, "w", encoding="utf-8") as f:
            f.write(text.strip())

        print(f"OCR sonucu kaydedildi: {txt_yolu}")
    except Exception as e:
        print(f"OCR sırasında hata oluştu: {e}")
