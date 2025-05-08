from PIL import Image
import pytesseract
import os

def perform_ocr():
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    INPUT_FOLDER = "girdi_klasoru"
    OUTPUT_FOLDER = "cikti_klasoru"
    SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

    image_file = None
    for file in os.listdir(INPUT_FOLDER):
        if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
            image_file = file
            break

    if not image_file:
        return "Error: No valid image found in the input folder."
    
    image_path = os.path.join(INPUT_FOLDER, image_file)

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="tur")

        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        txt_name = os.path.splitext(image_file)[0] + ".txt"
        txt_path = os.path.join(OUTPUT_FOLDER, txt_name)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text.strip())

        return f"OCR result has been saved: {txt_path}"
    except Exception as e:
        return f"An error occurred during OCR: {e}"