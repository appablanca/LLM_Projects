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
            json_final_response = json.loads(final_response)
            return jsonify({"success": True, "response": json_final_response["natural_response"]})


        # Handle Job 2: Already in natural language
        elif decision_json["job"] == "natural_response":
            return jsonify({"success": True, "response": decision_json["natural_response"]})

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
    
if __name__ == "__main__":
    print("Starting Flask server on port 5001...")
    app.run(debug=True, port=5001, host="0.0.0.0")
