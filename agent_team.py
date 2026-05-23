import os
import json
import openai

os.environ["OPENAI_API_KEY"] = "APIKEY HERE"

client = openai.OpenAI()

# ============================================================
# THE SHARED WHITEBOARD
# Both agents read and write here
# ============================================================

def create_state(topic):
    return {
        "topic": topic,        # what user asked
        "plan": [],            # planner writes here
        "results": [],         # executor writes here
        "final_output": ""     # final combined answer
    }

# ============================================================
# AGENT 1 — THE PLANNER
# Only job: break topic into learning steps
# Does NOT teach anything itself
# ============================================================
def planner_agent(state):
    print("\n[PLANNER] Thinking about how to teach:", state["topic"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a Java learning planner. 
Your ONLY job is to break a Java topic into exactly 4 learning steps.
Return ONLY a JSON array of 4 steps. Nothing else. No explanation.
Example: ["Explain the concept simply", "Show a code example", 
          "Show a common mistake", "Give one quiz question"]"""
            },
            {
                "role": "user",
                "content": f"Create a 4-step learning plan for: {state['topic']}"
            }
        ]
    )

    raw = response.choices[0].message.content.strip()

    # remove markdown code blocks if present
    raw = raw.replace("```json", "").replace("```", "").strip()

    plan = json.loads(raw)
    state["plan"] = plan

    print(f"[PLANNER] Created {len(plan)} step plan:")
    for i, step in enumerate(plan):
        print(f"          Step {i+1}: {step}")

    return state

# ============================================================
# AGENT 2 — THE EXECUTOR
# Only job: execute each step from the plan
# Does NOT plan anything
# ============================================================

def executor_agent(state):
    print("\n[EXECUTOR] Starting execution of plan...")

    for i, step in enumerate(state["plan"]):
        print(f"\n[EXECUTOR] Working on Step {i+1}: {step}")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a Java teaching executor.
You receive one specific teaching task and execute it perfectly.
Be clear, practical, and use simple language.
For code examples use proper Java syntax.
Keep each response focused and under 150 words."""
                },
                {
                    "role": "user",
                    "content": f"""Topic: {state['topic']}
Your specific task: {step}
Execute this task now."""
                }
            ]
        )

        result = response.choices[0].message.content.strip()
        state["results"].append({
            "step": i + 1,
            "task": step,
            "output": result
        })

        print(f"[EXECUTOR] Step {i+1} complete")

    return state

# ============================================================
# COMBINER — joins all results into final lesson
# ============================================================

def combine_results(state):
    print("\n[COMBINER] Building final lesson...")

    output = f"\n{'='*50}\n"
    output += f"JAVA LESSON: {state['topic'].upper()}\n"
    output += f"{'='*50}\n"

    for result in state["results"]:
        output += f"\n--- Step {result['step']}: {result['task']} ---\n"
        output += f"{result['output']}\n"

    output += f"\n{'='*50}\n"
    state["final_output"] = output
    return state

# ============================================================
# MAIN PIPELINE — runs both agents in sequence
# ============================================================

def teach(topic):
    # Step 1 — create empty whiteboard
    state = create_state(topic)

    # Step 2 — planner fills the plan
    state = planner_agent(state)

    # Step 3 — executor executes each step
    state = executor_agent(state)

    # Step 4 — combine into final lesson
    state = combine_results(state)

    return state["final_output"]

# ============================================================
# MAIN LOOP
# ============================================================

print("Java Multi-Agent Learning Coach ready!")
print("I will plan AND teach any Java topic you want.\n")

while True:
    topic = input("You: ")
    if topic.lower() == "quit":
        break

    print(teach(topic))