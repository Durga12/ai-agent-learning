import os
import json
from dotenv import load_dotenv
import openai

load_dotenv()
client = openai.OpenAI()
os.environ["OPENAI_API_KEY"] = "APIKEY HERE"

# ============================================================
# SHARED STATE — the whiteboard
# ============================================================

def create_state(java_code, filename):
    return {
        "filename":  filename,
        "code":      java_code,
        "problems":  [],
        "reviews":   [],
        "report":    ""
    }

# ============================================================
# AGENT 1 — READER
# Reads the Java code and finds all problems
# Does NOT suggest fixes — only finds issues
# ============================================================

def reader_agent(state):
    print("\n[READER] Analysing Java code...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a senior Java code reader.
Your ONLY job is to identify problems in Java code.
Find ALL of these: bugs, null pointer risks, performance issues, 
bad practices, missing error handling, security risks.
Return ONLY a JSON array of problems. Each problem has:
- "id": number starting from 1
- "type": one of [Bug, Performance, Security, BadPractice, NullRisk]
- "line_area": brief description of where in code
- "description": what the problem is in simple terms
Return ONLY the JSON array. No explanation. No markdown."""
            },
            {
                "role": "user",
                "content": f"Find all problems in this Java code:\n\n{state['code']}"
            }
        ]
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    problems = json.loads(raw)
    state["problems"] = problems

    print(f"[READER] Found {len(problems)} problems")
    for p in problems:
        print(f"         #{p['id']} {p['type']}: {p['description'][:60]}...")

    return state

# ============================================================
# AGENT 2 — REVIEWER
# Takes each problem and writes a specific fix
# ============================================================

def reviewer_agent(state):
    print(f"\n[REVIEWER] Writing fixes for {len(state['problems'])} problems...")

    for problem in state["problems"]:
        print(f"\n[REVIEWER] Fixing #{problem['id']}: {problem['type']}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a senior Java developer writing code reviews.
For each problem give:
1. Why this is a real problem (1-2 sentences)
2. The corrected Java code snippet
3. One sentence explaining what you changed
Be specific. Be practical. Use proper Java syntax."""
                },
                {
                    "role": "user",
                    "content": f"""Java code being reviewed:
{state['code']}

Problem to fix:
Type: {problem['type']}
Location: {problem['line_area']}
Description: {problem['description']}

Write the detailed review and fix."""
                }
            ]
        )

        review = response.choices[0].message.content.strip()
        state["reviews"].append({
            "problem_id": problem["id"],
            "type":       problem["type"],
            "location":   problem["line_area"],
            "description": problem["description"],
            "fix":        review
        })

    print(f"[REVIEWER] All {len(state['reviews'])} fixes written")
    return state

# ============================================================
# AGENT 3 — RANKER
# Ranks all problems by severity and writes final report
# ============================================================

def ranker_agent(state):
    print("\n[RANKER] Ranking problems and building report...")

    all_reviews = json.dumps(state["reviews"], indent=2)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a tech lead writing a final code review report.
Rank all problems as: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
Write a professional report with:
1. Executive Summary (2-3 sentences)
2. Problems ranked by severity with their fixes
3. Final recommendation
Use clear formatting. Be direct and actionable."""
            },
            {
                "role": "user",
                "content": f"""File reviewed: {state['filename']}

Here are all the problems and fixes found:
{all_reviews}

Write the final ranked code review report."""
            }
        ]
    )

    state["report"] = response.choices[0].message.content.strip()
    print("[RANKER] Report complete")
    return state

# ============================================================
# MAIN PIPELINE
# ============================================================

def review_file(filepath):
    print(f"\nReading file: {filepath}")

    with open(filepath, "r") as f:
        java_code = f.read()

    filename = filepath.split("\\")[-1].split("/")[-1]
    print(f"File: {filename} ({len(java_code)} characters)")

    state = create_state(java_code, filename)
    state = reader_agent(state)
    state = reviewer_agent(state)
    state = ranker_agent(state)

    return state["report"]

# ============================================================
# MAIN LOOP
# ============================================================

print("Java Code Review Agent 🔍")
print("Paste the path to your Java file for review.\n")

while True:
    filepath = input("File path (or 'quit'): ").strip()
    if filepath.lower() == "quit":
        break
    if not filepath.endswith(".java"):
        print("Please provide a .java file")
        continue
    try:
        report = review_file(filepath)
        print("\n" + "="*60)
        print(report)
        print("="*60)

        # Save report to file
        report_file = filepath.replace(".java", "_review.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")

    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except Exception as e:
        print(f"Error: {e}")