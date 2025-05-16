async def generate_life_plan(user, asking_question: bool = False):
    model = genai.GenerativeModel('gemini-pro')

    age = user.get("age", "not specified")
    income = user.get("income", 0)
    expenses = user.get("expenses", 0)
    savings = user.get("savings", 0)
    debts = user.get("debts", {})
    assets = user.get("assets", {})
    goals = user.get("goals", [])

    if asking_question:
        prompt = f"""
You are a smart financial assistant helping users build a personal life plan.

The user's goals include: {', '.join(goals) if goals else 'not specified'}

Before generating a full plan, ask a short and relevant clarifying question that will help improve the life plan. 
Example: "For your car goal, are you considering an SUV or a sedan?"

❗Your task: Ask **only one** specific question. Do **not** provide any explanation or context. Ask the question **in Turkish**.
"""
        response = model.generate_content(prompt)
        return {
            "questionMode": True,
            "question": response.text.strip()
        }

    prompt = f"""
You are a smart financial advisor. Based on the user's financial details, generate a comprehensive life plan.

User's profile:
- Age: {age}
- Monthly income: ${income}
- Monthly expenses: ${expenses}
- Current savings: ${savings}
- Debts: {debts}
- Assets: {assets}
- Goals: {', '.join(goals) if goals else 'not specified'}

📌 Please provide the life plan in **English** and use **clear numbers** in each section.
Structure your response in the following format:

🚗 Car Plan:
- How much should be saved, and over how long?
- What brand/model/year do you suggest?
- Average cost?

🏠 Housing Plan:
- When should the user buy a house?
- Which city/district would you recommend?
- Average cost and suggested down payment?

📈 Investment Plan:
- Recommended monthly investment amount?
- Which instruments (e.g. stocks, crypto, mutual funds)?

👶 Children Plan (if applicable):
- Suggestions for education funding?

🧓 Retirement Plan:
- Suggested retirement age?
- Target savings goal?
"""
    response = model.generate_content(prompt)
    return {
        "questionMode": False,
        "plan": response.text.strip()
    }
