# my_agent/utils/nodes.py
'''
import os
import re
import sqlite3
from functools import lru_cache
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from my_agent.utils.db import DB_PATH
from langgraph.prebuilt import ToolNode
from my_agent.utils.tools import tools

# Load environment variables
load_dotenv()

# ─── Shared SQLite Connection ─────────────────────────────────────────────────────────
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_cursor = _conn.cursor()

# ─── LLM Getter ────────────────────────────────────────────────────────────────────────
@lru_cache(maxsize=4)
def _get_llm():
    return AzureChatOpenAI(
        api_key        = os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version    = os.getenv("AZURE_OPENAI_API_VERSION"),
        deployment_name= os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        model_kwargs   = {"temperature": 0},
    )

# Optional: if you need tool routing
tool_node = ToolNode(tools)

# ─── Planner Agent ────────────────────────────────────────────────────────────────────
def planner_agent(state, config):
    """
    Decide whether to generate SQL or explain results.
    """
    prompt = SystemMessage(
        content="Reply exactly 'generate_sql' to produce SQL, or 'explain_results' to explain."
    )
    llm = _get_llm()
    res: AIMessage = llm.invoke(state["messages"] + [prompt])
    return {"messages": [AIMessage(content=res.content.strip().lower())]}

# ─── SQL Agent ────────────────────────────────────────────────────────────────────────
def sql_agent(state, config):
    """
    Generate a SQL query (with schema), extract and run only the first statement,
    then return the real results.
    """
    # 1) Provide your exact schema to the model
    schema = (
        "-- Schema:\n"
        "users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT)\n"
        "orders(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, total REAL)\n\n"
    )
    prompt = SystemMessage(
        content=(
            schema +
            "Generate only a valid SQL SELECT query for the user's request, "
            "using the exact schema above. End your response with 'Done.'"
        )
    )

    # 2) Invoke LLM
    llm = _get_llm()
    res: AIMessage = llm.invoke(state["messages"] + [prompt])
    raw = res.content

    # 3) Extract SQL (from ```sql``` fences or by cleaning lines)
    m = re.search(r"```sql\s*([\s\S]+?)```", raw, re.IGNORECASE)
    if m:
        sql = m.group(1).strip()
    else:
        lines = raw.splitlines()
        cleaned = []
        for line in lines:
            low = line.strip().lower()
            if low in ("sql", "```sql", "```") or "done." in low:
                continue
            if line.strip():
                cleaned.append(line)
        sql = "\n".join(cleaned).strip()

    # 4) Only keep the first statement to avoid multi-statement errors
    parts = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
    first_sql = parts[0]

    # 5) Execute and format results
    try:
        _cursor.execute(first_sql)
        rows = _cursor.fetchall()
        headers = [col[0] for col in _cursor.description]
        if rows:
            sep  = " | ".join(headers)
            dash = " | ".join("---" for _ in headers)
            data = "\n".join(" | ".join(str(c) for c in row) for row in rows)
            table = f"{sep}\n{dash}\n{data}"
        else:
            table = "No rows returned."
    except Exception as e:
        table = f"Error executing SQL: {e}"

    # 6) Return the SQL and the real results
    content = (
        f"```sql\n{first_sql}\n```  \n"
        f"**Results:**\n{table}\n\nDone."
    )
    return {"messages": [AIMessage(content=content)]}

# ─── Explainer Agent ─────────────────────────────────────────────────────────────────
def explainer_agent(state, config):
    """
    Explain the SQL query and its results in simple terms.
    """
    prompt = SystemMessage(
        content="Explain the SQL and the results in simple terms. End with 'Done.'"
    )
    llm = _get_llm()
    res: AIMessage = llm.invoke(state["messages"] + [prompt])
    return {"messages": [AIMessage(content=res.content)]}

# ─── Routing Logic ────────────────────────────────────────────────────────────────────
def decide_next_step(state):
    """
    Route based on the planner's choice token.
    """
    last_ai = next(m for m in reversed(state["messages"]) if isinstance(m, AIMessage))
    token = last_ai.content.strip().lower()
    if token == "generate_sql":
        return "to_sql"
    if token == "explain_results":
        return "to_explainer"
    return "end"
'''
import os
import io
import base64
import sqlite3
from functools import lru_cache
from dotenv import load_dotenv

import pandas as pd
import matplotlib.pyplot as plt
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import ToolNode

from my_agent.utils.db import DB_PATH
from my_agent.utils.tools import tools

load_dotenv()

# Shared SQLite connection
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_cursor = _conn.cursor()

# LLM getter
@lru_cache(maxsize=4)
def _get_llm():
    return AzureChatOpenAI(
        api_key         = os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint  = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version     = os.getenv("AZURE_OPENAI_API_VERSION"),
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        model_kwargs    = {"temperature": 0},
    )

# Optional: route external tools
tool_node = ToolNode(tools)


def planner_agent(state, config):
    prompt = SystemMessage(
        content="Reply exactly 'generate_sql', 'explain_results', or 'visualize_results'."
    )
    llm = _get_llm()
    res = llm.invoke(state["messages"] + [prompt])
    return {"messages":[AIMessage(content=res.content.strip().lower())]}


def extract_sql(raw: str) -> str:
    """Extract first ```sql ... ``` fenced block."""
    low = raw.lower()
    start = low.find("```sql")
    if start == -1:
        return ""
    start = raw.find("\n", start) + 1
    end = raw.find("```", start)
    return raw[start:end].strip() if end != -1 else raw[start:].strip()


def sql_agent(state, config):
    schema = (
        "-- Schema:\n"
        "users(id INTEGER PRIMARY KEY, name TEXT, email TEXT)\n"
        "orders(id INTEGER PRIMARY KEY, user_id INTEGER, total REAL)\n\n"
    )
    prompt = SystemMessage(
        content=(
            schema
            + "Generate only a valid SQL SELECT query for the user's request, "
            + "using the exact schema above. End your response with 'Done.'"
        )
    )
    llm = _get_llm()
    res = llm.invoke(state["messages"] + [prompt])

    raw_sql = extract_sql(res.content)
    if not raw_sql:
        return {"messages":[AIMessage(content="Error: no SQL found.")]}

    first_sql = raw_sql.split(";",1)[0].strip()
    try:
        _cursor.execute(first_sql)
        rows = _cursor.fetchall()
        headers = [c[0] for c in _cursor.description] or []
        if rows and headers:
            sep = " | ".join(headers)
            dash = " | ".join("---" for _ in headers)
            data = "\n".join(" | ".join(str(v) for v in row) for row in rows)
            table_md = f"{sep}\n{dash}\n{data}"
        else:
            table_md = "No rows returned."
    except Exception as e:
        table_md = f"Error executing SQL: {e}"

    content = (
        f"```sql\n{first_sql}\n```\n\n"
        f"**Results:**\n{table_md}\n\nDone."
    )
    return {"messages":[AIMessage(content=content)]}


def explainer_agent(state, config):
    prompt = SystemMessage(
        content="Explain the SQL and the results in simple terms. End with 'Done.'"
    )
    llm = _get_llm()
    res = llm.invoke(state["messages"] + [prompt])
    return {"messages":[AIMessage(content=res.content.strip())]}


# This will be wired from agent.py
tracer = None

def visualize_agent(state, config):
    # 1) extract last SQL
    last = next((m for m in reversed(state["messages"]) if "```sql" in m.content), None)
    if not last:
        return {"messages":[AIMessage(content="No previous SQL found.")]}
    sql = extract_sql(last.content)
    if not sql:
        return {"messages":[AIMessage(content="Could not extract SQL.")]}

    # 2) load into DataFrame
    df = pd.read_sql_query(sql, _conn)

    # 3) markdown table
    hdr = df.columns.tolist()
    sep = " | ".join(hdr)
    dash = " | ".join("---" for _ in hdr)
    rows_md = "\n".join(" | ".join(str(x) for x in row) for row in df.values)
    table_md = f"{sep}\n{dash}\n{rows_md}"

    # 4) plot & embed as base64
    df2 = df.set_index(hdr[0])
    numeric = df2.select_dtypes("number")

    buf = io.BytesIO()
    if not numeric.empty:
        ax = numeric.plot(kind="bar").axes
        plt.tight_layout()
        plt.savefig(buf, format="png")
    else:
        fig, ax = plt.subplots()
        ax.text(0.5,0.5,"No numeric columns to chart",ha="center",va="center")
        plt.tight_layout()
        fig.savefig(buf, format="png")
    plt.close()

    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("ascii")
    img_md = f"![chart](data:image/png;base64,{img_b64})"

    content = (
        f"```sql\n{sql}\n```\n\n"
        f"**Results:**\n{table_md}\n\n"
        f"{img_md}"
    )
    return {"messages":[AIMessage(content=content)]}


def decide_next_step(state):
    last = next(m for m in reversed(state["messages"]) if isinstance(m, AIMessage))
    tok = last.content.strip().lower()
    if tok == "generate_sql":
        return "sql_agent"
    if tok == "explain_results":
        return "explainer"
    if tok == "visualize_results":
        return "visualizer"
    return "end"
