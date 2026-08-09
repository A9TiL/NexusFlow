import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from app.db.session import SessionLocal
from app.tools.database_tools import get_server_status, get_network_logs, create_support_ticket
from pydantic import BaseModel, Field


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH, override=True)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file.")


class ServerStatusInput(BaseModel):
    node_id: int = Field(description="The numeric ID of the server node (e.g., 1, 12, 14)")

class NetworkLogsInput(BaseModel):
    node_id: int = Field(description="The numeric ID of the server node")
    limit: int = Field(default=5, description="Number of recent log entries to retrieve")

class SupportTicketInput(BaseModel):
    node_id: int = Field(description="The numeric ID of the degraded server node")
    issue: str = Field(description="Clear description of the detected issue")
    priority: str = Field(description="Ticket priority level: 'Low', 'Medium', or 'High'")

@tool (args_schema=ServerStatusInput)
def tool_get_server_status(node_id: int) -> dict:
    """Fetches the current status and region of a specific server node."""
    db = SessionLocal()
    try:
        return get_server_status(db, node_id)
    finally:
        db.close()

@tool (args_schema=NetworkLogsInput)
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


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=api_key
)


system_prompt = "You are an enterprise IT multi-agent orchestrator. Always use the provided tools to check server statuses, network logs, and create tickets. If a node is failing, create a high-priority ticket."

agent_executor = create_react_agent(llm, tools, prompt=system_prompt)

def run_orchestrator(user_prompt: str) -> str:
    """Invokes the LangGraph state machine with terminal observability."""
    inputs = {"messages": [("user", user_prompt)]}
    
    print("\n" + "="*50)
    print("AGENT REASONING LOOP START")
    print("="*50)
    
    final_message = ""
    
    for chunk in agent_executor.stream(inputs, stream_mode="values"):
        latest_msg = chunk["messages"][-1]
        
        latest_msg.pretty_print() 
        
        final_message = latest_msg.content
        
    print("="*50)
    print("AGENT REASONING LOOP COMPLETE")
    print("="*50 + "\n")
    
    return final_message