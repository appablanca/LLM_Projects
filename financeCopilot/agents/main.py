import os, sys, json
import google.generativeai as genai
from flask import send_file
from agents.baseAgent import Agent
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent, normalChatAgentRole
from agents.orcestratorAgent import Orcestrator, orcestratorAgentRole, agents
from agents.lifePlannerAgent import LifePlannerAgent, lifePlannerAgentRole
from agents.budgetPlannerAgent import BudgetPlannerAgent, budgetPlannerAgentRole
from agents.investmentAdvisorAgent import InvestmentAdvisorAgent, investmentAdvisorAgentRole
from agents.exportReportAgent import generate_transaction_pdf, generate_budget_pdf
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from agents.job_tracking import job_status
from flask import Flask, jsonify
import time
import yfinance as yf
import asyncio


app = Flask(__name__)

# More permissive CORS configuration
CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    },
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

orchestrator = Orcestrator("Orchestrator", orcestratorAgentRole)
budget_planner = BudgetPlannerAgent("BudgetPlannerAgent", budgetPlannerAgentRole)


@app.route("/chat", methods=["POST", "OPTIONS"])
def handle_user_input():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response

    try:
        user_text = request.form.get("message")
        uploaded_file = request.files.get("file")
        user = request.form.get("user")

        if not user_text and not uploaded_file:
            return jsonify({"success": False, "message": "Message or file is required"}), 400


        track_id = "static-track-id"
        if track_id in job_status:
            del job_status[track_id]
        job_status[track_id] = {"status": "processing", "step": "routing to agent", "user_input": user_text}

        # Step 1: Get orchestrator job decision
        orchestrator_decision = orchestrator.model.generate_content(user_text)
        print(f"🧠 Orchestrator decision: {orchestrator_decision.text}")

        decision_json = json.loads(orchestrator_decision.text)

        # Handle Job 1: Routing
        if decision_json["job"] == "routing":
            selected_agent_key = decision_json["selected_agent"]

            if selected_agent_key not in agents:
                return jsonify({"success": False, "message": f"Unknown agent: {selected_agent_key}"}), 400

            print(f"📬 Routing to: {selected_agent_key}")
            agent = agents[selected_agent_key]

            # Handle file input (only valid for expenseAnalyzerAgent)
            if selected_agent_key == "expenseanalyzeragent":
                if uploaded_file and uploaded_file.filename:
                    result = agent.categorize_pdf(uploaded_file)
                else:
                    return jsonify({"success": False, "message": "Please upload a PDF file for analysis"}), 400

            # Handle async agents
            elif selected_agent_key == "lifeplanneragent":
                result = asyncio.run(agent.get_life_plan(user_text, user))

            elif selected_agent_key == "investmentadvisoragent":
                result = asyncio.run(agent.get_financal_advise(user_text, user))

            # Handle synchronous agents
            else:
                result = agent.generate_response(user_text)

            # Save history
            orchestrator.conversation_history.append({
                "user_input": user_text,
                "agent_key": selected_agent_key,
                "agent_response": result
            })

            # Step 2: Get final natural language response from orchestrator
            final_response = orchestrator.generate_final_response(user_text, result)
            print(f"📦 Raw orchestrator response: {final_response}")

            if not final_response:
                return jsonify({"success": False, "message": "Orchestrator failed to generate final response"}), 500

            try:
                if isinstance(final_response, str):
                    parsed_response = json.loads(final_response)
                else:
                    parsed_response = final_response

                agent_resp = parsed_response.get("agent_response")
                if isinstance(agent_resp, str):
                    extra_parsed = json.loads(agent_resp)
                else:
                    extra_parsed = agent_resp
            except Exception as parse_err:
                print(f"🧨 JSON parse error: {parse_err}")
                print(f"📝 Raw final_response: {final_response}")
                return jsonify({
                    "success": False,
                    "message": "Final response could not be parsed",
                    "error": str(parse_err),
                }), 500

            return jsonify({"success": True, "response": extra_parsed})


        # Handle Job 2: Already in natural language
        elif decision_json["job"] == "transporting":
            return jsonify({"success": True, "response": decision_json["transporting"]})

        else:
            return jsonify({"success": False, "message": "Invalid job type from orchestrator"}), 400

    except Exception as e:
        print(f"Error in handle_user_input: {e}")
        return jsonify({
            "success": False,
            "message": "An error occurred while processing your request",
            "error": str(e),
        }), 500

@app.route("/budget-analysis", methods=["POST", "OPTIONS"])
def handle_budget_analysis():
    """
    Endpoint to handle budget analysis requests.
    """
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response

    try:
        userId = request.json.get("userId")

        if not userId:
            return jsonify({"success": False, "message": "userId is required"}), 400

        result = budget_planner.run_budget_analysis(userId)

        if not result:
            return jsonify({"success": False, "message": "No data available for analysis"}), 404

        return jsonify({"success": True, "response": result})

    except Exception as e:
        print(f"Error in handle_budget_analysis: {e}")
        return jsonify({
            "success": False,
            "message": "An error occurred while processing your request",
            "error": str(e)
        }), 500


@app.route("/embeddings", methods=["POST"])
def get_embeddings():
    try:
        data = request.get_json()
        text = data.get("text")

        if not text:
            return jsonify({"success": False, "message": "Text is required"}), 400

        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )

        return jsonify({"success": True, "embeddings": result["embedding"]})

    except Exception as e:
        print(f"Error in get_embeddings: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "error": str(e)
        }), 500

# New endpoint: Get job status
@app.route("/job-status/<job_id>", methods=["GET"])
def get_job_status(job_id):
    job = job_status.get(job_id)
    if not job:
        return jsonify({
            "success": True,
            "status": {
                "status": "idle",
                "step": "waiting for input"
            }
        })
    return jsonify({"success": True, "status": job})



@app.route("/export-transaction", methods=["POST"])
def transaction_export():
    data = request.get_json()
    path = generate_transaction_pdf(data)
    return send_file(path, as_attachment=True)

@app.route("/export-budget", methods=["POST"])
def budget_export():
    data = request.get_json()
    path = generate_budget_pdf(data)
    return send_file(path, as_attachment=True)

def get_current_market_prices_fast(file_path: str):
    with open(file_path, "r") as f:
        symbols = [line.strip() for line in f if line.strip()]

    data = yf.download(
        tickers=" ".join(symbols),
        period="1d",
        interval="1m",  
        group_by="ticker",
        threads=True,
        progress=False
    )

    results = []
    for symbol in symbols:
        try:
            last_price = data[symbol]["Close"].dropna().iloc[-1]
            results.append(f"{symbol}: {last_price:.2f} $")
        except Exception:
            results.append(f"{symbol}: Price not available")

    return results

@app.route("/market-prices", methods=["GET"])
def fetch_market_prices():
    start = time.time()
    prices = get_current_market_prices_fast("./agents/financeAgent/sp500_symbols.txt")
    elapsed = time.time() - start

    with open("./agents/financeAgent/market_prices_output.txt", "w") as f:
        for p in prices:
            f.write(p + "\n")
        f.write(f"\nExecution Time: {elapsed:.2f} seconds\n")

    return jsonify({"status": "success", "method": "yfinance", "execution_time": elapsed}), 200
"""
#TEST İÇİN POSTMAN İLE DENEME KISMI

import base64

@app.route("/test-export-transaction-preview", methods=["POST"])
def test_transaction_preview():
    data = request.get_json()
    path = generate_transaction_pdf(data)

    with open(path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode("utf-8")

    return jsonify({
        "success": True,
        "filename": "transaction_report.pdf",
        "base64_pdf": encoded_pdf
    })
"""


if __name__ == "__main__":
    print("Starting Flask server on port 5001...")
    app.run(debug=True, port=5001, host="0.0.0.0")

