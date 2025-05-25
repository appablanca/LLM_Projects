import os
import json
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv
import unicodedata

# Kullanıcıya gösterilecek tüm metinleri Latin-1 karakter setine uyarlayan fonksiyon Türkçe karakterlerdeki sorunu kaldırmak için
def normalize_text(text):
    if isinstance(text, str):
        return unicodedata.normalize("NFKD", text).encode("latin-1", "ignore").decode("latin-1")
    return text

# Ortam değişkenlerinden API anahtarını yükler
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

llm_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": 0.4,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 2048
    }
)

# LLM ile transaction verisinden metinsel özet üretir
def generate_summary_from_transactions(data):
    prompt = f"""
You are a financial assistant. Below is a credit card transaction summary for a user.
Based on the provided JSON, summarize the user's spending habits, major expense categories, 
and areas to watch out for in approximately 300 words.

Please start your summary like this:
"Dear {data.get('customer_info', {}).get('full_name', 'customer')}, after reviewing your account activity..."

JSON:
{json.dumps(data, indent=2)}
"""
    response = llm_model.generate_content(prompt)
    return response.text.strip()

# Kullanıcı bilgisine göre kişisel bir giriş paragrafı hazırlar
def generate_intro_from_user_info(user_info):
    name = user_info.get("name", "User")
    income = user_info.get("income", "Not provided")
    city = user_info.get("location", "Unknown")
    return f"Dear {name}, after analyzing your financial information, here are some suggestions based on your income and spending habits. City: {city}, Monthly Income: {income} TL\n\n"

# Kategori bazlı harcamaları pie chart olarak çizer
def generate_pie_chart(category_totals):
    labels = []
    values = []
    for cat, amount in category_totals.items():
        try:
            val = float(amount.replace(".", "").replace(",", ".").replace(" TL", ""))
            label = normalize_text(cat.replace("_", " ").title())
            labels.append(label)
            values.append(val)
        except:
            continue

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")

    path = os.path.join(tempfile.gettempdir(), "pie_chart.png")
    plt.savefig(path)
    plt.close()
    return path

# Aylık harcamaları kategoriye göre bar chart olarak çizer
def generate_bar_chart_over_time(spending_over_time):
    categories = set()
    for month_data in spending_over_time.values():
        categories.update(month_data.keys())

    months = sorted(spending_over_time.keys())
    category_values = {cat: [] for cat in categories}
    for month in months:
        for cat in categories:
            value = spending_over_time[month].get(cat, 0)
            category_values[cat].append(value)

    fig, ax = plt.subplots()
    bar_width = 0.1
    x = list(range(len(months)))

    for idx, (cat, vals) in enumerate(category_values.items()):
        ax.bar(
            [i + idx * bar_width for i in x],
            vals,
            width=bar_width,
            label=normalize_text(cat)
        )

    ax.set_xticks([i + bar_width for i in x])
    ax.set_xticklabels(months, rotation=45)
    ax.set_ylabel("Spending (TL)")
    ax.set_title("Monthly Spending by Category")
    ax.legend()

    path = os.path.join(tempfile.gettempdir(), "bar_chart_time.png")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path

# Aylık net tasarrufu (gelir - gider) line chart ile gösterir
def generate_net_difference_line_chart(monthly_data):
    months = sorted(monthly_data.keys())
    net_diff = [monthly_data[m]["income"] - monthly_data[m]["expenses"] for m in months]

    fig, ax = plt.subplots()
    ax.plot(months, net_diff, marker="o")
    ax.set_title("Monthly Net Savings (Income - Expenses)")
    ax.set_ylabel("Net Amount (TL)")
    ax.set_xlabel("Month")
    ax.grid(True)

    path = os.path.join(tempfile.gettempdir(), "net_trend_line.png")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path

# PDF'ye tablo olarak öneri/hacama tablosunu ekler
def add_suggestions_table_to_pdf(pdf, table_data):
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Category", border=1)
    pdf.cell(50, 10, "Total Spent", border=1)
    pdf.cell(80, 10, "Suggestion", border=1)
    pdf.ln()

    pdf.set_font("Arial", size=11)
    for row in table_data:
        pdf.cell(60, 10, normalize_text(row["category"]), border=1)
        pdf.cell(50, 10, normalize_text(row["total_spent"]), border=1)
        pdf.cell(80, 10, normalize_text(row["suggestion"]), border=1)
        pdf.ln()

# Transaction tabanlı PDF rapor oluşturur (özet, pasta grafik, öneri tablosu)
def generate_transaction_pdf(data):
    summary = generate_summary_from_transactions(data)
    summary = normalize_text(summary)

    chart_path = generate_pie_chart(data.get("category_totals", {}))

    pdf = FPDF()
    pdf.add_page()

    # Summary yazısı
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)
    pdf.ln(10)

    # Pie chart
    if os.path.exists(chart_path):
        pdf.image(chart_path, x=30, w=150)
        pdf.ln(15)

    # Harcama/Suggestion tablosu
    table_data = []
    category_totals = data.get("category_totals", {})
    # Örnek öneriler: Geliştirilebilir ya da gerçek transaction verisinden türetilebilir
    for category, total in category_totals.items():
        suggestion = "Consider reducing this category if possible."
        if "grocery" in category.lower():
            suggestion = "Plan weekly meals, buy in bulk"
        elif "entertainment" in category.lower():
            suggestion = "Limit to 10% of income"
        elif "transport" in category.lower():
            suggestion = "Use public transport or shared rides"
        elif "subscriptions" in category.lower():
            suggestion = "Cancel unused subscriptions"
        elif "food" in category.lower():
            suggestion = "Try cooking at home"

        table_data.append({
            "category": category.title(),
            "total_spent": total,
            "suggestion": suggestion
        })

    # Tablo başlığı
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Category", border=1)
    pdf.cell(50, 10, "Total Spent", border=1)
    pdf.cell(80, 10, "Suggestion", border=1)
    pdf.ln()

    # Satırlar
    pdf.set_font("Arial", size=11)
    for row in table_data:
        pdf.cell(60, 10, normalize_text(row["category"]), border=1)
        pdf.cell(50, 10, normalize_text(row["total_spent"]), border=1)
        pdf.cell(80, 10, normalize_text(row["suggestion"]), border=1)
        pdf.ln()

    output_path = os.path.join(tempfile.gettempdir(), "transaction_report.pdf")
    pdf.output(output_path)
    return output_path

# Bütçe planlaması tabanlı PDF rapor üretir (giriş, grafikler, öneriler, tablo)
def generate_budget_pdf(data):
    user_info = data.get("user_info", {})
    intro = normalize_text(generate_intro_from_user_info(user_info))

    spending_over_time = data.get("spending_over_time", {})
    monthly_data = data.get("monthly_net_data", {})

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, intro)
    pdf.ln(10)  # Intro'dan sonra boşluk

    # 🔹 Bar Chart (Spending over time)
    if spending_over_time:
        bar_chart_path = generate_bar_chart_over_time(spending_over_time)
        if os.path.exists(bar_chart_path):
            pdf.image(bar_chart_path, x=10, w=180)
            pdf.ln(15)  # Grafik sonrası boşluk

    # 🔹 Line Chart (Net savings trend)
    if monthly_data:
        line_chart_path = generate_net_difference_line_chart(monthly_data)
        if os.path.exists(line_chart_path):
            pdf.image(line_chart_path, x=10, w=180)
            pdf.ln(15)  # Grafik sonrası boşluk

    # 🔹 Category-based improvement recommendations
    recs_by_category = {}
    for rec in data.get("improvement_recommendations", []):
        lowered = rec.lower()
        category = "General"
        if "transport" in lowered or "bus" in lowered or "taxi" in lowered:
            category = "Transportation"
        elif "food" in lowered or "groceries" in lowered:
            category = "Food"
        elif "entertainment" in lowered:
            category = "Entertainment"
        recs_by_category.setdefault(category, []).append(normalize_text(rec))

    for cat, recs in recs_by_category.items():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, normalize_text(f"{cat}:"), ln=True)
        pdf.set_font("Arial", size=11)
        for rec in recs:
            pdf.multi_cell(0, 10, f"- {normalize_text(rec)}")
        pdf.ln(4)

    # 🔹 Suggestions Table
    pdf.ln(10)
    table_data = [
        {"category": "Groceries", "total_spent": "3,200 TL", "suggestion": "Plan weekly meals, buy in bulk"},
        {"category": "Entertainment", "total_spent": "2,000 TL", "suggestion": "Limit to 10% of income"},
    ]
    add_suggestions_table_to_pdf(pdf, table_data)

    output_path = os.path.join(tempfile.gettempdir(), "budget_report.pdf")
    pdf.output(output_path)
    return output_path
