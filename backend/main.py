from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Access expense_agent_free.py from parent folder
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from expense_agent import (
    make_expense,
    policy_check,
    anomaly_detection,
    agent_decision
)

app = FastAPI(
    title="Smart Expense Approval Agent",
    description="AI-powered expense approval API",
    version="1.0"
)

# CORS - allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store previous expenses for anomaly detection
expense_history = []


class ExpenseRequest(BaseModel):
    emp_id: str
    name: str
    amount: float
    category: str
    description: str
    date: str
    has_preapproval: bool = False


@app.get("/")
def home():
    return {
        "message": "Smart Expense Approval Agent API is running",
        "status": "success"
    }


@app.post("/analyze")
def analyze_expense(expense_data: ExpenseRequest):

    global expense_history

    # Create expense
    expense = make_expense(
        expense_data.emp_id,
        expense_data.name,
        expense_data.amount,
        expense_data.category,
        expense_data.description,
        expense_data.date,
        expense_data.has_preapproval
    )

    # Check company policy
    violations = policy_check(expense)

    # Check current expense against previous expenses
    all_expenses = expense_history + [expense]

    anomalies = anomaly_detection(
        expense,
        all_expenses
    )

    # Agent makes final decision
    result = agent_decision(
        expense,
        violations,
        anomalies
    )

    # Save expense for future comparisons
    expense_history.append(expense)

    return {
        "expense": expense,
        "policy_violations": violations,
        "anomalies": anomalies,
        "decision": result
    }
