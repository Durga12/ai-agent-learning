# AI Agent Learning Journey 🤖

> Java developer (8 years) transitioning to AI Engineering.  
> Building real projects from scratch — not tutorials, not copies.

## Projects Built

### Week 3 — Java Interview Q&A Bot (RAG System)
**File:** `rag_bot.py`

A Retrieval Augmented Generation bot that answers Java interview 
questions from its own knowledge base.

**What it does:**
- Converts Java Q&As into vector embeddings using OpenAI
- Stores and searches by meaning using ChromaDB (not keywords)
- Refuses to hallucinate — if answer not in data, says so
- Distance-based retrieval threshold prevents wrong answers

**What I learned:**
- Data quality is 80% of RAG — bad data = bad answers always
- Distance scores reveal retrieval confidence (below 0.3 = excellent)
- System prompt guardrails control hallucination completely
- Semantic search finds meaning even when words don't match

**Tech stack:** Python · OpenAI API · ChromaDB · text-embedding-3-small

---

### Week 4 — Java AI Agent with Tool Calling
**File:** `tool_bot.py` *(coming soon)*

An AI agent that automatically picks the right tool based on 
the user's question — no if-else logic written by me.

**Tools:**
- `search_java_knowledge` — RAG bot from Week 3 as a tool
- `get_current_time` — timezone-aware time lookup  
- `calculate` — mathematical expressions

**What I learned:**
- LLM routes to correct tool automatically from descriptions
- System prompt discipline prevents rogue answers
- The entire RAG system becomes one tool in a bigger agent
- Tool quality determines answer quality — not the LLM

**Tech stack:** Python · OpenAI API · ChromaDB · pytz

---

## Setup

```bash
git clone https://github.com/Durga12/ai-agent-learning
cd ai-agent-learning
pip install openai chromadb tiktoken pytz python-dotenv
```

Create a `.env` file:
