import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from app.db.session import SessionLocal
from app.tools.database_tools import get_server_status, get_network_logs, create_support_ticket

# Load the environment variables (API Key)
load_dotenv()

# Tools for the LLM
# The LLM reads the docstrings of the function wrappers to understand what each tool does.
@tool
def tool_get_server_status(node_id: int) -> dict:
    """Fetches the current status and region of a specific server node."""
    db = SessionLocal()
    try:
        return get_server_status(db, node_id)
    finally:
        db.close()

@tool
def tool_get_network_logs(node_id: int, limit: int = 5) -> list:
    """Retrieves recent diagnostic logs for a server node to check for latency or errors."""
    db = SessionLocal()
    try:
        return get_network_logs(db, node_id, limit)
    finally:
        db.close()

@tool
def tool_create_support_ticket(node_id: int, issue: str, priority: str) -> dict:
    """Logs a new support ticket into the system for a failing or degraded node."""
    db = SessionLocal()
    try:
        return create_support_ticket(db, node_id, issue, priority)
    finally:
        db.close()


tools = [tool_get_server_status, tool_get_network_logs, tool_create_support_ticket]

# LLM Configuration and initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    temperature=0, 
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# The Orchestration Prompt 
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an enterprise IT multi-agent orchestrator. You have access to database tools to check server statuses, retrieve network logs, and create support tickets. Always use the provided tools to answer the user's request. If a node is failing or has high latency, automatically generate a high-priority support ticket."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

#  The ReAct Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# verbose=True will print the Thought -> Action -> Observation loop in the terminal
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_orchestrator(user_prompt: str) -> str:
    """Entry point to trigger the agent loop from the FastAPI route."""
    response = agent_executor.invoke({"input": user_prompt})
    return response["output"]