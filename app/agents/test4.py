from phi.agent import Agent, AgentMemory
from phi.model.ollama import Ollama
from phi.tools.sql import SQLTools
from phi.tools.postgres import PostgresTools
from phi.storage.agent.postgres import PgAgentStorage

db_url="postgresql+psycopg://postgres:1234@localhost:5432/knowledge_base"

postgres_tools = PostgresTools(
    host="localhost",
    port=5432,
    db_name="knowledge_base",
    user="postgres", 
    password="1234"
)
storage = PgAgentStorage(
    table_name="clinic_chat_sessions",
    db_url=db_url,
)

agent = Agent(
    model=Ollama(id="clinic_llama32"),
    name="Agent",
    # role="Interact with the database",
    # tools=[postgres_tools],
    # storage=storage,
    # show_tool_calls=True
)

#agent.print_response("Insert a new item into the 'items' table with name 'Example Item' and price 19.99")