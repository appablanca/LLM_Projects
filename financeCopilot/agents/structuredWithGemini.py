import os
import json
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyC9Eh9t8QeLoPKI7d8Sw6x0qr4qVyT9QH4"
genai.configure(api_key=GOOGLE_API_KEY)

INPUT_FOLDER = "cikti_klasoru"
OUTPUT_FOLDER = "structured_output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

txt_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".txt")]
if not txt_files:
    raise FileNotFoundError("cikti_klasoru içinde .txt dosyası bulunamadı.")
input_path = os.path.join(INPUT_FOLDER, txt_files[0])

with open(input_path, "r", encoding="utf-8") as f:
    raw_text = f.read()

model = genai.GenerativeModel("gemini-2.0-flash")

system_prompt = f"""
Sen bir metin yapılandırma asistanısın. Aşağıda verilen ham metni incele ve bunu aşağıdaki JSON şemasına göre formatla.

Kurallar:
1. "türü", "musteri_bilgileri", "islemler", "kart_limiti", "kategori_toplamlari" ana alanlarını mutlaka oluştur.
2. Tüm para değerlerini TL olarak bırak ve aynen aktar (virgül ve nokta biçimleri korunmalı).
3. "islemler" kısmındaki her satırı dikkatli ayır: tarih, açıklama, tutar ve varsa maxipuan.
4. "kategori_toplamlari" kısmında verilen kategorilere göre toplamları sınıflandır. Kategori listesi aşağıda.
5. Bilgi eksikse null değeri kullan.
6. JSON biçimi geçerli ve düzenli olmalı.

Kategoriler:
["yeme_icme", "giyim_kozmetik", "abonelik", "market", "ulasim", "eglence", "kirtasiye_kitap", "teknoloji", "fatura_odeme", "egitim", "saglik", "nakit_cekme", "diger"]

JSON Formatı:
{{
  "türü": "fiş/fatura/hesap dökümü",
  "musteri_bilgileri": {{
    "ad_soyad": "MELİSA SUBAŞI"
  }},
  "islemler": [...],
  "kart_limiti": {{
    "toplam_kart_limiti": "2.000,00 TL",
    ...
  }},
  "kategori_toplamlari": {{
    "yeme_icme": "1.819,00 TL",
    ...
  }}
}}
Şu metni dönüştür:
{raw_text}
"""
response = model.generate_content(system_prompt)

cleaned_text = response.text.strip().strip("`").strip()
if cleaned_text.startswith("json"):
    cleaned_text = cleaned_text[4:].strip()

try:
    json_data = json.loads(cleaned_text)
except json.JSONDecodeError as e:
    print("JSON format hatası:", e)
    print("Yanıt içeriği:\n", response.text)
    raise

output_path = os.path.join(OUTPUT_FOLDER, "output.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print(f"JSON dosyası başarıyla kaydedildi: {output_path}")
