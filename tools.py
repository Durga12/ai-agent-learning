import os
import json
import datetime
import openai

os.environ["OPENAI_API_KEY"] = "apikey"
client = openai.OpenAI()

# ============================================================
# STEP 1 — Define your tools (the toolbox)
# ============================================================

tools = [
    {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Returns the current date and time for a given timezone. Use this when user asks about time or date anywhere in the world.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone name like Asia/Kolkata for India, America/New_York for US East, America/Los_Angeles for US West, Europe/London for UK, Asia/Tokyo for Japan"
                }
            },
            "required": ["timezone"]
        }
    }
},
    {
        "type": "function",
        "function": {
            "name": "search_java_knowledge",
            "description": "Searches Java knowledge base to answer Java programming questions about OOP, exceptions, collections, threads, streams.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The Java topic or question to search for"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Performs mathematical calculations. Use this for any arithmetic the user asks for.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to calculate. Example: 847 * 23"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# ============================================================
# STEP 2 — Write the actual tool functions (real Python code)
# ============================================================
def get_current_time(timezone="Asia/Kolkata"):
    import pytz
    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz)
    return f"Current time in {timezone}: {now.strftime('%A, %d %B %Y, %I:%M %p %Z')}"


def search_java_knowledge(query):
    java_knowledge = [
        "Q: How do strings compare in Java? What is == vs equals? How to compare string values?\nA: == checks reference equality meaning same memory address. .equals() checks value equality meaning same content. Always use .equals() for String comparison.",

        "Q: What is NullPointerException? What happens when I call method on null? How to avoid NPE?\nA: NPE happens when you call a method on a null object reference. Avoid with null checks using if(obj != null), use Optional<T>, or Objects.requireNonNull().",

        "Q: What is the difference between ArrayList and LinkedList? Which is faster for index access?\nA: ArrayList uses dynamic array, O(1) random access, slow insert/delete in middle. LinkedList uses doubly linked nodes, O(1) insert/delete, slow random access. Use ArrayList for most cases.",

        "Q: What are four pillars of OOP? Explain encapsulation inheritance polymorphism abstraction.\nA: Encapsulation hides data behind methods. Inheritance lets child class extend parent. Polymorphism means same method behaves differently per object. Abstraction hides complexity.",

        "Q: What is HashMap and how does it work internally? How does hashing work in Java?\nA: HashMap stores key-value pairs using hashing. hashCode() finds bucket, equals() resolves collisions. Default capacity 16, load factor 0.75.",

        "Q: What is difference between abstract class and interface in Java?\nA: Abstract class can have state and method bodies, single inheritance only. Interface is pure contract, multiple implementation allowed. Use interface for capability, abstract for shared base.",

        "Q: What is garbage collection in Java? How does JVM free memory?\nA: JVM automatically frees unused objects. GC runs when heap is full using mark-and-sweep. You cannot force it but can suggest with System.gc().",

        "Q: What is volatile keyword in Java? How does volatile work with threads?\nA: volatile ensures variable is always read from main memory not CPU cache. Changes visible to all threads immediately. Lighter than synchronized but only for single variable visibility.",

        "Q: What is difference between checked and unchecked exceptions in Java?\nA: Checked exceptions must be declared or caught like IOException. Unchecked extend RuntimeException like NullPointerException, no forced handling.",

        "Q: What is Java Stream API? How do streams work in Java 8?\nA: Stream API allows functional-style processing. filter() selects, map() transforms, reduce() combines, collect() gathers. Lazy evaluation, can be parallel with parallelStream().",
    ]

    import chromadb
    chroma = chromadb.Client()

    try:
        collection = chroma.get_collection("java_tool_qa")
    except:
        collection = chroma.create_collection("java_tool_qa")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=java_knowledge
        )
        vectors = [item.embedding for item in response.data]
        collection.add(
            documents=java_knowledge,
            embeddings=vectors,
            ids=[str(i) for i in range(len(java_knowledge))]
        )

    q_response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    q_vector = q_response.data[0].embedding

    results = collection.query(query_embeddings=[q_vector], n_results=2)
    best_distance = results["distances"][0][0]

    if best_distance > 0.8:
        return "No relevant Java information found for that query."

    return "\n---\n".join(results["documents"][0])


def calculate(expression):
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Could not calculate: {str(e)}"


# ============================================================
# STEP 3 — The tool runner (maps name → actual function)
# ============================================================

def run_tool(tool_name, tool_args):
    print(f"\n[AGENT] Calling tool: {tool_name} with args: {tool_args}")

    if tool_name == "get_current_time":
        timezone = tool_args.get("timezone", "Asia/Kolkata")
        return get_current_time(timezone)

    elif tool_name == "search_java_knowledge":
        return search_java_knowledge(tool_args["query"])

    elif tool_name == "calculate":
        return calculate(tool_args["expression"])

    else:
        return f"Unknown tool: {tool_name}"


# ============================================================
# STEP 4 — The agent loop (the brain)
# ============================================================

def ask(question):
    messages = [
        {"role": "system", "content": """You are a Java assistant. You have exactly 3 tools.
STRICT RULES:
1. For ANY Java question — always call search_java_knowledge first
2. If the tool returns 'No relevant information found' — say exactly: 'I don't have that in my knowledge base yet.'
3. NEVER answer Java questions from your own knowledge. Only from tool results.
4. For time questions — use get_current_time tool
5. For math — use calculate tool
6. For anything else — say 'I can only help with Java, time, and math.'"""},       
        {"role": "user", "content": question}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # Case 1 — LLM wants to call a tool
        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                tool_result = run_tool(tool_name, tool_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

        # Case 2 — LLM has final answer, stop looping
        else:
            return message.content


# ============================================================
# STEP 5 — Main chat loop
# ============================================================

print("Java Agent ready! I have tools for time, Java knowledge, and math.\n")
while True:
    q = input("You: ")
    if q.lower() == "quit":
        break
    print(f"\nBot: {ask(q)}\n")
