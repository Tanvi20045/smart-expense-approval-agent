# Smart Expense Approval Agent
**AIONOS Agentic AI Factory — Internship Submission**

## Problem
Finance teams manually review every employee expense claim against policy
rules, hunting for anomalies by eye. It's slow and error-prone at scale.

## Solution
An agentic AI tool that processes each claim through four reasoning stages —
not a single-shot yes/no classifier:

```
 Expense Claim
      │
      ▼
 ① Policy Check ───────────► deterministic rule engine
      │                       (limits per category, pre-approval rules)
      ▼
 ② Anomaly Detection ──────► pattern checks across the employee's claims
      │                       (same-day duplicates, weekends, round numbers,
      │                        outlier amounts vs. category median)
      ▼
 ③ Agent Decision ─────────► Claude reasons over the rule + anomaly output
      │                       and decides: APPROVE / REJECT / FLAG_FOR_MANAGER
      │                       with a plain-English justification
      ▼
 ④ Monthly Summary Report ─► category-wise spend, decision breakdown,
                              list of every flagged/rejected item
```

## Why this is "agentic" and not just a chatbot
Steps ① and ② are deterministic and auditable — Finance can see exactly
which rule or pattern triggered. Step ③ is where Claude adds judgment: it
weighs ambiguous cases (e.g. a weekend claim with an otherwise-clean policy
record) the way a human reviewer would, rather than a rigid if/else block.
The agent explains *why*, which is what a rule-only script can't do.

## Tech stack
- Python 3.9+
- `anthropic` SDK (official Claude API client)
- No web framework needed — runs as a terminal demo, keeping setup to
  under a minute for the judges.

## Setup
```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."   # Windows: set ANTHROPIC_API_KEY=...
python expense_agent.py
```

## Demo script (3-4 sample claims, live)
| # | Employee | Claim | Expected outcome | Why |
|---|----------|-------|-------------------|-----|
| 1 | Priya Sharma | ₹850 meal | **APPROVE** | Under daily limit, no anomalies |
| 2 | Rahul Verma | ₹18,000 flight | **REJECT** | Over ₹10k travel threshold, no pre-approval |
| 3 | Ananya Iyer | ₹1,950 keyboard | **FLAG** | Just under the ₹2,000 limit + weekend date |
| 4 | Karan Mehta | ₹1,500 + ₹1,000 meals, same day | **FLAG** | Two same-day claims trigger the anomaly detector |

## Company policy rules encoded
- Meals: ≤ ₹1,500/day
- Travel: > ₹10,000 needs pre-approval
- Office Supplies: ≤ ₹2,000/item
- Client Entertainment: ≤ ₹5,000/day
- Software/Subscriptions: > ₹3,000/month needs IT approval

## Possible next steps (mention in Q&A if asked)
- Swap the in-memory `SAMPLE_EXPENSES` list for a real DB / Google Sheet of
  historical claims so anomaly detection has true history, not just the batch.
- Add a Slack/email notification step when a claim is flagged.
- Add a simple Streamlit front-end if a visual demo is preferred over terminal.
