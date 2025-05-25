import sys
import os
import json
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

from agents.job_tracking import job_status
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import uuid

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
    """
    Chat bot endpoint to handle user input and return a response.
    """
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
            return jsonify({"success": False, "track_id": None, "message": "Message or file is required"}), 400

        track_id = "static-track-id"
        if track_id in job_status:
            del job_status[track_id]
        job_status[track_id] = {"status": "processing", "step": "routing to agent", "user_input": user_text}

        agent_key = orchestrator.get_agent_key(user_text).lower()
        job_status[track_id]["step"] = f"agent routing: {agent_key}"
        print(f"📎 Uploaded file: {uploaded_file.filename if uploaded_file else 'None'}")

        if agent_key in agents:
            print(f"Selected Agent: {agent_key}")

            if agent_key == "expenseanalyzeragent":
                if uploaded_file and uploaded_file.filename:
                    try:
                        job_status[track_id]["step"] = "running expense analyzer agent"
                        result = agents[agent_key].categorize_pdf(uploaded_file)
                        orchestrator.conversation_history.append(
                            {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
                        )
                        job_status[track_id].update({"status": "done", "step": "completed", "response": result})
                        return jsonify({"success": True, "track_id": track_id, "response": result})
                    except Exception as e:
                        print(f"🚫 Error processing file: {str(e)}")
                        job_status[track_id].update({"status": "failed", "step": "error", "error": str(e)})
                        return jsonify({
                            "success": False,
                            "track_id": track_id,
                            "message": "Error processing the file",
                            "error": str(e),
                        }), 500
                else:
                    job_status[track_id].update({"status": "failed", "step": "waiting for PDF", "error": "No file uploaded"})
                    return jsonify({
                        "success": False,
                        "track_id": track_id,
                        "message": "Please upload a PDF file for analysis",
                    }), 400

            elif agent_key == "lifeplanneragent":
                job_status[track_id]["step"] = "running life planner agent"
                result = asyncio.run(agents[agent_key].get_life_plan(user_text, user))
                orchestrator.conversation_history.append(
                    {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
                )
                job_status[track_id].update({"status": "done", "step": "completed", "response": result})
                return jsonify({"success": True, "track_id": track_id, "response": result})

            elif agent_key == "investmentadvisoragent":
                job_status[track_id]["step"] = "running investment advisor agent"
                result = asyncio.run(agents[agent_key].get_financal_advise(user_text,user))
                orchestrator.conversation_history.append(
                    {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
                )
                job_status[track_id].update({"status": "done", "step": "completed", "response": result})
                return jsonify({"success": True, "track_id": track_id, "response": result})

            else:
                job_status[track_id]["step"] = f"running {agent_key}"
                result = agents[agent_key].generate_response(user_text)
                orchestrator.conversation_history.append(
                    {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
                )
                job_status[track_id].update({"status": "done", "step": "completed", "response": result})
                return jsonify({"success": True, "track_id": track_id, "response": result})

        # fallback: bilinmeyen agent
        print("⚠️ Unknown agent key:", agent_key)
        result = agents["normalchatagent"].generate_response(user_text)
        orchestrator.conversation_history.append(
            {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
        )
        job_status[track_id].update({"status": "done", "step": "fallback to normal agent", "response": result})
        return jsonify({"success": True, "track_id": track_id, "response": result})

    except Exception as e:
        print(f"Error in handle_user_input: {e}")
        job_status[track_id].update({"status": "failed", "step": "error", "error": str(e)})
        return jsonify({
            "success": False,
            "track_id": track_id,
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
