import streamlit as st
import os
import json
from dotenv import load_dotenv
import openai

load_dotenv()
client = openai.OpenAI(api_key=st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"))

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Java Code Review Agent",
    page_icon="☕",
    layout="wide"
)

# ============================================================
# HEADER
# ============================================================

st.title("☕ Java Code Review Agent")
st.markdown("**Built by Durga — Java Tech Lead turned AI Engineer**")
st.markdown("Paste any Java code below and get a professional AI-powered review instantly.")
st.divider()

# ============================================================
# THE 3 AGENTS — same as code_reviewer.py
# ============================================================

def reader_agent(code):
    with st.spinner("🔍 Agent 1: Reading and finding problems..."):
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
                    "content": f"Find all problems in this Java code:\n\n{code}"
                }
            ]
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)


def reviewer_agent(code, problems):
    reviews = []
    total = len(problems)
    progress = st.progress(0, text="Agent 2: Writing fixes...")

    for i, problem in enumerate(problems):
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
{code}

Problem to fix:
Type: {problem['type']}
Location: {problem['line_area']}
Description: {problem['description']}

Write the detailed review and fix."""
                }
            ]
        )
        reviews.append({
            "problem_id": problem["id"],
            "type":       problem["type"],
            "location":   problem["line_area"],
            "description": problem["description"],
            "fix":        response.choices[0].message.content.strip()
        })
        progress.progress((i + 1) / total,
                         text=f"Agent 2: Fixed {i+1} of {total} problems...")

    return reviews


def ranker_agent(reviews):
    with st.spinner("📊 Agent 3: Ranking and writing final report..."):
        all_reviews = json.dumps(reviews, indent=2)
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
                    "content": f"Here are all problems and fixes:\n{all_reviews}\n\nWrite the final ranked report."
                }
            ]
        )
        return response.choices[0].message.content.strip()

# ============================================================
# UI LAYOUT
# ============================================================

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Your Java Code")
    java_code = st.text_area(
        "Paste your Java code here",
        height=400,
        placeholder="""public class Example {
    public String getName(Map<String, String> user) {
        return user.get("name").toUpperCase(); // NPE risk!
    }
}"""
    )

    review_button = st.button(
        "🔍 Review My Code",
        type="primary",
        use_container_width=True
    )

with col2:
    st.subheader("📋 Review Report")

    if review_button:
        if not java_code.strip():
            st.error("Please paste some Java code first!")
        else:
            try:
                # Run all 3 agents
                problems  = reader_agent(java_code)
                st.success(f"✅ Found {len(problems)} problems")

                reviews   = reviewer_agent(java_code, problems)
                report    = ranker_agent(reviews)

                # Show the report
                st.markdown(report)

                # Download button
                st.divider()
                st.download_button(
                    label="⬇️ Download Report",
                    data=report,
                    file_name="java_code_review.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.info("👈 Paste your Java code on the left and click Review My Code")
        st.markdown("""
**What this agent checks:**
- 🔴 Security vulnerabilities
- 🟠 Bugs and null pointer risks
- 🟡 Performance issues
- 🟢 Bad practices and code smells

**How it works:**
1. Reader Agent finds all problems
2. Reviewer Agent writes specific fixes
3. Ranker Agent ranks by severity
        """)

# ============================================================
# FOOTER
# ============================================================

st.divider()
st.markdown(
    "Built with Python · OpenAI · Streamlit · "
    "[GitHub](https://github.com/Durga12/ai-agent-learning)",
    unsafe_allow_html=False
)