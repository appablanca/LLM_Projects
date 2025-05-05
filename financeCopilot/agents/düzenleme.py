import os
import json
import google.generativeai as genai

# API key ayarı
genai.configure(api_key="YOUR_GEMINI_API_KEY")

INPUT_FOLDER = "cikti_klasoru"
OUTPUT_FOLDER = "kategorize_jsonlar"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Gemini modelini başlat
model = genai.GenerativeModel("gemini-pro")

# Prompt formatı
def build_prompt(json_text):
    return f"""
Aşağıda kredi kartı ekstre verisi var. Lütfen şu formatta yeniden yapılandır:

- "type": fiş mi ekstre mi belirt
- "tarih": varsa hesap kesim tarihi
- "total_harcama": altına kategorize ederek gruplandır:
    - yeme içme
    - giyim aksesuar
    - hobi oyun eğlence
    - market
    - tatil seyahat
    - ev
    - sağlık kişisel bakım
    - diğer

Her harcamayı en uygun kategoriye koy. Format JSON olsun.

Veri:
{json_text}
"""

# Her dosyayı işle
def process_files():
    for filename in os.listdir(INPUT_FOLDER):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(INPUT_FOLDER, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        prompt = build_prompt(json.dumps(raw_data, ensure_ascii=False, indent=2))
        try:
            response = model.generate_content(prompt)
            result = response.text

            # Eğer yanıt düzgün JSON değilse pars etmeye çalışırız
            try:
                parsed_json = json.loads(result)
            except:
                # Temizlemek gerekirse buraya eklenebilir
                parsed_json = result

            output_path = os.path.join(OUTPUT_FOLDER, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed_json, f, ensure_ascii=False, indent=4)

            print(f"✔ Düzenlendi: {filename}")

        except Exception as e:
            print(f"⚠ Hata oluştu: {filename} → {e}")

if __name__ == "__main__":
    process_files()
