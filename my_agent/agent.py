# my_agent/agent.py
'''
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from my_agent.utils.nodes import (
    planner_agent,
    sql_agent,
    explainer_agent,
    decide_next_step
)
from my_agent.utils.state import AgentState

class GraphConfig(TypedDict):
    model_name: Literal["azure_openai"]

workflow = StateGraph(AgentState, config_schema=GraphConfig)

# Register the three agents
workflow.add_node("planner", planner_agent)
workflow.add_node("sql_agent", sql_agent)
workflow.add_node("explainer", explainer_agent)

# Start here
workflow.set_entry_point("planner")

# Route based on planner's exact token
workflow.add_conditional_edges(
    "planner",
    decide_next_step,
    {
        "to_sql": "sql_agent",
        "to_explainer": "explainer",
        "end": END
    }
)

# No add_edge calls—after each chosen node, graph will end automatically

graph = workflow.compile()

# (Optional) LangSmith tracing
from langchain_core.tracers.langchain import LangChainTracer
import os
tracer = LangChainTracer(project_name=os.getenv("LANGCHAIN_PROJECT", "langgraph-azure-gpt4o"))
graph = graph.with_config({"callbacks": [tracer]})
from my_agent.utils.db import init_database
init_database()'''

# my_agent/agent.py

# my_agent/agent.py

# my_agent/agent.py

# my_agent/agent.py

import os
from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END
from langchain_core.tracers.langchain import LangChainTracer as LangSmithTracer

import my_agent.utils.nodes as nodes
from my_agent.utils.nodes import (
    planner_agent,
    sql_agent,
    explainer_agent,
    visualize_agent,
    decide_next_step
)
from my_agent.utils.state import AgentState

class GraphConfig(TypedDict):
    model_name: Literal["azure_openai"]

# 1) LangSmith tracer
tracer = LangSmithTracer(project_name=os.getenv("LANGCHAIN_PROJECT", "langgraph-azure-gpt4o"))

# 2) Build workflow
workflow = StateGraph(AgentState, config_schema=GraphConfig)
workflow.add_node("planner",    planner_agent)
workflow.add_node("sql_agent",  sql_agent)
workflow.add_node("explainer",  explainer_agent)
workflow.add_node("visualizer", visualize_agent)
workflow.set_entry_point("planner")

workflow.add_conditional_edges(
    "planner",
    decide_next_step,
    {
        "sql_agent":   "sql_agent",
        "explainer":   "explainer",
        "visualizer":  "visualizer",
        "end":         END
    }
)

# chain SQL→visualize
workflow.add_edge("sql_agent", "visualizer")

# 3) compile with tracer
graph = workflow.compile().with_config({"callbacks": [tracer]})

# 4) wire tracer into visualize_agent
nodes.tracer = tracer

# 5) initialize DB
from my_agent.utils.db import init_database
init_database()
