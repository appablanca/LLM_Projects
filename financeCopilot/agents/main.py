import os, sys, json
import google.generativeai as genai
from agents.baseAgent import Agent
from agents.expenseAnalyzerAgent import ExpenseAnalyzerAgent, expenseAnalyzerRole
from agents.normalChatAgent import NormalChatAgent, normalChatAgentRole
from agents.orcestratorAgent import Orcestrator, orcestratorAgentRole, agents
from agents.lifePlannerAgent import LifePlannerAgent, lifePlannerAgentRole
from agents.budgetPlannerAgent import BudgetPlannerAgent, budgetPlannerAgentRole
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

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

        if not user_text and not uploaded_file:
            return jsonify({"success": False, "message": "Message or file is required"}), 400

        agent_key = orchestrator.get_agent_key(user_text).lower()
        print(f"📎 Uploaded file: {uploaded_file.filename if uploaded_file else 'None'}")

        if agent_key in agents:
            print(f"Selected Agent: {agent_key}")

            if agent_key == "expenseanalyzeragent":
                if uploaded_file and uploaded_file.filename:
                    try:
                        result = agents[agent_key].categorize_pdf(uploaded_file)
                        orchestrator.conversation_history.append(
                            {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
                        )
                        return jsonify({"success": True, "response": result})
                    except Exception as e:
                        print(f"🚫 Error processing file: {str(e)}")
                        return jsonify({
                            "success": False,
                            "message": "Error processing the file",
                            "error": str(e),
                        }), 500
                else:
                    return jsonify({
                        "success": False,
                        "message": "Please upload a PDF file for analysis",
                    }), 400

            elif agent_key == "lifeplanneragent":
                result = asyncio.run(agents[agent_key].get_life_plan(user_text))
                orchestrator.conversation_history.append(
                    {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
                )
                return jsonify({"success": True, "response": result})

            elif agent_key == "investmentadvisoragent":
                result = asyncio.run(agents[agent_key].get_financal_advise())
                orchestrator.conversation_history.append(
                    {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
                )
                return jsonify({"success": True, "response": result})

            else:
                result = agents[agent_key].generate_response(user_text)
                orchestrator.conversation_history.append(
                    {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
                )
                return jsonify({"success": True, "response": result})

        # fallback: bilinmeyen agent
        print("⚠️ Unknown agent key:", agent_key)
        result = agents["normalchatagent"].generate_response(user_text)
        orchestrator.conversation_history.append(
            {"user_input": user_text, "agent_key": agent_key, "agent_response": result}
        )
        return jsonify({"success": True, "response": result})

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


if __name__ == "__main__":
    print("Starting Flask server on port 5001...")
    app.run(debug=True, port=5001, host="0.0.0.0")
