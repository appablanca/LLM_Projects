import os
import io
import re
import tempfile
import matplotlib.pyplot as plt
from fpdf import FPDF
from dotenv import load_dotenv
import google.generativeai as genai

# == Ortam değişkenleri ==
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# == Font yolu ==
FONT_PATH = "C:/Windows/Fonts/arial.ttf"

# == PDF sınıfı ==
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("ArialUnicode", "", FONT_PATH, uni=True)
        self.set_font("ArialUnicode", size=12)

# == Markdown temizleyici ==
def clean_markdown(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    return text


def generate_gemini_comment_for_budget(data: dict) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are an AI financial analyst. A user's monthly budget data is provided below.

    == Financial Summary ==
    {data.get("financial_summary", {})}

    == Spending Analysis ==
    {data.get("spending_analysis", [])}

    Based on this data, write a detailed and helpful budget analysis including:

    1. Overspending Alerts: Categories where the user is spending above average or disproportionately.
    2. Saving Suggestions: Realistic and specific ways the user could reduce spending or improve habits.
    3. Improvement Recommendations: Long-term strategies to optimize financial health.
    4. General Summary: Overall tone — is the user doing well? What should they focus on next month?

    Present each section with clear headings and bullet points. Avoid generic advice. Be personal and specific.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_pdf_for_budget_planner(data: dict) -> bytes:
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("ArialUnicode", size=14)
    pdf.cell(200, 10, txt="Budget Planning Report", ln=True, align="C")
    pdf.ln(10)

    # Kullanıcı bilgisi
    user_info = data.get("user_info", {})
    pdf.set_font("ArialUnicode", size=12)
    for k, v in user_info.items():
        pdf.cell(200, 10, txt=f"{k.capitalize()}: {v}", ln=True)
    pdf.ln(5)

    # Finansal özet
    summary = data.get("financial_summary", {})
    pdf.cell(200, 10, txt="Financial Summary", ln=True)
    for k, v in summary.items():
        pdf.cell(200, 10, txt=f"{k.replace('_', ' ').capitalize()}: {v}", ln=True)
    pdf.ln(5)

    # Harcama analizi grafiği
    analysis = data.get("spending_analysis", [])
    if analysis:
        categories = [x["category"] for x in analysis]
        amounts = [x["amount"] for x in analysis]
        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Spending Distribution")
        chart_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        plt.savefig(chart_path)
        plt.close()
        pdf.image(chart_path, x=30, y=pdf.get_y(), w=150)
        pdf.ln(90)

    # AI yorumları ayrı sayfada
    pdf.add_page()
    pdf.set_font("ArialUnicode", size=14)
    pdf.cell(200, 10, txt="AI Commentary", ln=True)
    pdf.set_font("ArialUnicode", size=11)

    comment = generate_gemini_comment_for_budget(data)
    clean_comment = clean_markdown(comment)
    for line in clean_comment.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

def generate_pdf_for_life_plan(data: dict, user_info: dict = None) -> bytes:
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("ArialUnicode", size=14)
    pdf.cell(200, 10, txt="Life Planning Report", ln=True, align="C")
    pdf.ln(10)

    # Kullanıcı bilgisi
    if user_info:
        pdf.set_font("ArialUnicode", size=12)
        for k, v in user_info.items():
            pdf.cell(200, 10, txt=f"{k.capitalize()}: {v}", ln=True)
        pdf.ln(5)

    # Plan bölümleri
    plan = data.get("lifePlan", {})
    fields = [
        ("Goal", plan.get("goal")),
        ("Estimated Cost", plan.get("estimatedCost")),
        ("Timeline", plan.get("timeline")),
        ("Monthly Plan", plan.get("monthlyPlan")),
        ("General Summary", plan.get("generalSummeryOfPlan"))
    ]

    for title, content in fields:
        if content:
            pdf.set_font("ArialUnicode", size=12)
            pdf.cell(200, 10, txt=title, ln=True)
            pdf.set_font("ArialUnicode", size=11)
            for line in clean_markdown(content).split('\n'):
                pdf.multi_cell(0, 10, line)
            pdf.ln(5)

    # Öneriler
    recommendations = plan.get("recommendations", [])
    if recommendations:
        pdf.set_font("ArialUnicode", size=12)
        pdf.cell(200, 10, txt="Recommendations", ln=True)
        pdf.set_font("ArialUnicode", size=11)
        for rec in recommendations:
            pdf.multi_cell(0, 10, f"- {clean_markdown(rec)}")
        pdf.ln(5)

    # Byte olarak çıktı ver
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

""""
# == TEST ==
if __name__ == "__main__":
    def test_export_budget():
        sample_data = {
            "user_info": {
                "name": "Ayşe Yılmaz",
                "age": 28,
                "location": "İstanbul",
                "rent": 6000,
                "income": 20000,
                "occupation": "Digital Marketing Specialist"
            },
            "financial_summary": {
                "monthly_income": 20000,
                "total_spending": 19200,
                "net_difference": 800,
                "summary_comment": "Your spending is slightly high this month."
            },
            "spending_analysis": [
                {"category": "Groceries", "amount": 4200, "income_ratio_percent": 21.0, "comment": "Well-managed."},
                {"category": "Transportation", "amount": 1800, "income_ratio_percent": 9.0, "comment": "Efficient usage."},
                {"category": "Entertainment", "amount": 2700, "income_ratio_percent": 13.5, "comment": "Above recommended."},
                {"category": "Dining Out", "amount": 1600, "income_ratio_percent": 8.0, "comment": "Moderate."},
                {"category": "Clothing", "amount": 1300, "income_ratio_percent": 6.5, "comment": "Typical seasonal."}
            ]
        }

        pdf_bytes = generate_pdf_for_budget_planner(sample_data)
        with open("test_budget_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("✅ test_budget_output.pdf başarıyla oluşturuldu.")

    test_export_budget()
"""
if __name__ == "__main__":
    def test_export_life_plan():
        sample_life_data = {
            "lifePlan": {
                "goal": "Buy a 2nd-hand C-segment car in 2 years",
                "estimatedCost": "1,000,000 – 1,200,000 TRY",
                "timeline": "24 months – Save 30,000 TRY/month",
                "monthlyPlan": "Cut back on dining out, limit shopping, redirect 30k/month to savings.",
                "generalSummeryOfPlan": "A disciplined savings approach that lets you buy a car without debt.",
                "recommendations": [
                    "Switch from Uber to public transport, save ~1,200 TRY/month.",
                    "Shop once every 3 months instead of monthly.",
                    "Avoid weekend impulse buys.",
                    "Consider Toyota Corolla, Renault Megane, or Fiat Egea.",
                    "Track weekly progress using a spreadsheet or mobile app."
                ]
            }
        }

        user = {
            "name": "Ayşe Yılmaz",
            "age": 28,
            "location": "İstanbul",
            "income": "20,000 TRY",
            "occupation": "Digital Marketing Specialist"
        }

        pdf_bytes = generate_pdf_for_life_plan(sample_life_data, user)
        with open("test_life_plan_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("✅ test_life_plan_output.pdf başarıyla oluşturuldu.")

    test_export_life_plan()