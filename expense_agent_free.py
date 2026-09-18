"""
Smart Expense Approval Agent — FREE / OFFLINE VERSION
========================================================
An agentic AI tool that processes employee expense claims through
multi-step autonomous reasoning: Policy Check -> Anomaly Detection ->
Weighted Reasoning Engine -> Decision + Justification -> Monthly Report.

NO API KEY NEEDED. NO COST. Runs 100% locally.

The "agentic" part: instead of a single if/else, the agent builds a
reasoning trace step by step (like a human reviewer would), assigns a
risk score based on multiple weighted signals, and only THEN reaches a
decision — with a full explanation of every factor it considered.

Requires: nothing beyond standard Python 3.9+ (no pip installs at all)

Run:       python expense_agent.py
"""

import json
from datetime import datetime
from collections import defaultdict

# ---------------------------------------------------------------------------
# STEP 0: CONFIG — Company Expense Policy Rules
# ---------------------------------------------------------------------------

POLICY_RULES = {
    "Meals": {
        "daily_limit": 1500,
        "rule_text": "Meals must not exceed ₹1500/day.",
    },
    "Travel": {
        "preapproval_threshold": 10000,
        "rule_text": "Travel expenses above ₹10,000 require prior manager pre-approval.",
    },
    "Office Supplies": {
        "per_item_limit": 2000,
        "rule_text": "Office supply items must not exceed ₹2000 each.",
    },
    "Client Entertainment": {
        "daily_limit": 5000,
        "rule_text": "Client entertainment must not exceed ₹5000/day.",
    },
    "Software/Subscriptions": {
        "monthly_limit": 3000,
        "rule_text": "Software subscriptions above ₹3000/month require IT approval.",
    },
}


# ---------------------------------------------------------------------------
# STEP 1: INPUT — Expense Claim Data Model
# ---------------------------------------------------------------------------

def make_expense(emp_id, name, amount, category, description, date, has_preapproval=False):
    return {
        "emp_id": emp_id,
        "name": name,
        "amount": amount,
        "category": category,
        "description": description,
        "date": date,  # "YYYY-MM-DD"
        "has_preapproval": has_preapproval,
    }


# ---------------------------------------------------------------------------
# STEP 2: POLICY CHECK
# ---------------------------------------------------------------------------

def policy_check(expense):
    violations = []
    category = expense["category"]
    amount = expense["amount"]
    policy = POLICY_RULES.get(category)

    if not policy:
        violations.append(f"No defined policy for category '{category}' — needs manual classification.")
        return violations

    if category == "Meals" and amount > policy["daily_limit"]:
        violations.append(f"Meal claim ₹{amount} exceeds daily limit of ₹{policy['daily_limit']}.")

    if category == "Travel" and amount > policy["preapproval_threshold"] and not expense["has_preapproval"]:
        violations.append(f"Travel claim ₹{amount} exceeds ₹{policy['preapproval_threshold']} and has no pre-approval on file.")

    if category == "Office Supplies" and amount > policy["per_item_limit"]:
        violations.append(f"Office supply item ₹{amount} exceeds per-item limit of ₹{policy['per_item_limit']}.")

    if category == "Client Entertainment" and amount > policy["daily_limit"]:
        violations.append(f"Client entertainment ₹{amount} exceeds daily limit of ₹{policy['daily_limit']}.")

    if category == "Software/Subscriptions" and amount > policy["monthly_limit"]:
        violations.append(f"Subscription ₹{amount} exceeds ₹{policy['monthly_limit']}/month threshold — needs IT approval.")

    return violations


# ---------------------------------------------------------------------------
# STEP 3: ANOMALY DETECTION
# ---------------------------------------------------------------------------

def anomaly_detection(expense, all_expenses):
    flags = []
    emp_claims = [e for e in all_expenses if e["emp_id"] == expense["emp_id"]]

    same_day = [e for e in emp_claims if e["date"] == expense["date"]]
    if len(same_day) > 1:
        flags.append(f"{len(same_day)} claims submitted by this employee on the same date ({expense['date']}).")

    try:
        weekday = datetime.strptime(expense["date"], "%Y-%m-%d").weekday()
        if weekday >= 5:
            flags.append("Claim dated on a weekend — verify business justification.")
    except ValueError:
        flags.append("Date could not be parsed — check format.")

    round_number_claims = [e for e in emp_claims if e["amount"] % 500 == 0]
    if len(round_number_claims) >= 2 and expense["amount"] % 500 == 0:
        flags.append("Repeated round-number amounts across this employee's claims — possible estimation rather than receipts.")

    cat_amounts = [e["amount"] for e in all_expenses if e["category"] == expense["category"]]
    if len(cat_amounts) >= 3:
        sorted_amts = sorted(cat_amounts)
        median = sorted_amts[len(sorted_amts) // 2]
        if median > 0 and expense["amount"] > 3 * median:
            flags.append(f"Amount is {round(expense['amount']/median, 1)}x the median for '{expense['category']}' claims in this batch.")

    return flags


# ---------------------------------------------------------------------------
# STEP 4: AGENT REASONING ENGINE (replaces the paid LLM call)
# ---------------------------------------------------------------------------
# This is the "brain" of the agent. It doesn't just check true/false rules —
# it weighs multiple signals together (like a human reviewer mentally
# weighing severity) and builds a step-by-step reasoning trace before
# reaching a decision. This is what makes it agentic rather than a plain
# rule lookup: the reasoning chain and the final call are both computed
# dynamically per-claim, not hardcoded per-category.

def agent_decision(expense, violations, anomalies):
    reasoning_trace = []
    risk_score = 0

    # Weight hard policy violations heavily
    for v in violations:
        risk_score += 40
        reasoning_trace.append(f"Policy violation detected: {v}")

    # Weight anomalies more lightly — suspicious, not necessarily wrong
    for a in anomalies:
        risk_score += 15
        reasoning_trace.append(f"Anomaly flagged: {a}")

    if not violations and not anomalies:
        reasoning_trace.append("No policy violations and no anomalies found — claim is clean.")

    # Decision thresholds
    if risk_score == 0:
        decision = "APPROVE"
        confidence = "High"
        summary = "No violations or anomalies detected; claim fully complies with policy."
    elif violations and risk_score >= 40 and not anomalies:
        # Clear-cut hard violation, no ambiguity → reject
        decision = "REJECT"
        confidence = "High"
        summary = "Claim breaches a hard policy limit with no mitigating anomaly context — rejected outright."
    else:
        # Anomalies present, or violations mixed with anomalies → needs human judgment
        decision = "FLAG_FOR_MANAGER"
        confidence = "Medium"
        summary = "Claim has ambiguous signals (violation and/or anomaly) that need human context before a final call."

    reasoning_text = summary + " " + " ".join(reasoning_trace) if reasoning_trace else summary

    return {
        "decision": decision,
        "reasoning": reasoning_text,
        "confidence": confidence,
        "risk_score": risk_score,
        "reasoning_trace": reasoning_trace,
    }


# ---------------------------------------------------------------------------
# STEP 5 (BONUS): MONTHLY SUMMARY REPORT
# ---------------------------------------------------------------------------

def generate_report(processed_expenses):
    lines = []
    lines.append("=" * 60)
    lines.append("MONTHLY EXPENSE SUMMARY REPORT")
    lines.append("=" * 60)

    category_totals = defaultdict(float)
    decision_counts = defaultdict(int)
    flagged_items = []

    for item in processed_expenses:
        e = item["expense"]
        d = item["agent_result"]
        category_totals[e["category"]] += e["amount"]
        decision_counts[d["decision"]] += 1
        if d["decision"] in ("REJECT", "FLAG_FOR_MANAGER"):
            flagged_items.append(item)

    lines.append("\n-- Category-wise Spend --")
    for cat, total in sorted(category_totals.items(), key=lambda x: -x[1]):
        lines.append(f"  {cat:<25} ₹{total:,.2f}")

    lines.append("\n-- Decision Breakdown --")
    for decision, count in decision_counts.items():
        lines.append(f"  {decision:<20} {count}")

    lines.append(f"\n-- Flagged / Rejected Items ({len(flagged_items)}) --")
    for item in flagged_items:
        e, d = item["expense"], item["agent_result"]
        lines.append(f"  [{d['decision']}] {e['name']} — ₹{e['amount']} ({e['category']}, {e['date']})")
        lines.append(f"      Reason: {d['reasoning']}")

    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ORCHESTRATOR — runs the full 4-step agent flow per expense
# ---------------------------------------------------------------------------

def process_expense(expense, all_expenses):
    violations = policy_check(expense)
    anomalies = anomaly_detection(expense, all_expenses)
    result = agent_decision(expense, violations, anomalies)
    return {
        "expense": expense,
        "violations": violations,
        "anomalies": anomalies,
        "agent_result": result,
    }


def print_result(item):
    e, d = item["expense"], item["agent_result"]
    print(f"\n{'-'*60}")
    print(f"Employee: {e['name']} ({e['emp_id']})")
    print(f"Claim: Rs.{e['amount']} | {e['category']} | {e['date']}")
    print(f"Description: {e['description']}")
    print(f"\nPolicy violations detected: {item['violations'] or 'None'}")
    print(f"Anomaly flags detected:     {item['anomalies'] or 'None'}")
    print(f"Risk score: {d['risk_score']}")
    print(f"\n>>> DECISION: {d['decision']}  (confidence: {d['confidence']})")
    print(f">>> REASONING: {d['reasoning']}")


# ---------------------------------------------------------------------------
# DEMO — 4-5 sample expenses covering different outcomes
# ---------------------------------------------------------------------------

SAMPLE_EXPENSES = [
    make_expense("E101", "Priya Sharma", 850, "Meals", "Team lunch with client", "2026-09-15"),
    make_expense("E102", "Rahul Verma", 18000, "Travel", "Flight to Bangalore for vendor visit",
                  "2026-09-16", has_preapproval=False),
    make_expense("E103", "Ananya Iyer", 1950, "Office Supplies", "Ergonomic keyboard", "2026-09-13"),
    make_expense("E104", "Karan Mehta", 1500, "Meals", "Client dinner", "2026-09-15"),
]

SAMPLE_EXPENSES.append(
    make_expense("E104", "Karan Mehta", 1000, "Meals", "Snacks during late work session", "2026-09-15")
)


def main():
    print("Smart Expense Approval Agent (FREE / OFFLINE) — processing sample claims...\n")

    processed = []
    for expense in SAMPLE_EXPENSES:
        item = process_expense(expense, SAMPLE_EXPENSES)
        print_result(item)
        processed.append(item)

    print("\n\n")
    print(generate_report(processed))


if __name__ == "__main__":
    main()
