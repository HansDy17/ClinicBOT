from phi.agent import Agent
from phi.model.ollama import Ollama
from os import getenv
from dotenv import load_dotenv
import mysql.connector
import psycopg2
from phi.memory.db.postgres import PgMemoryDb
from phi.tools.sql import SQLTools
from phi.tools.postgres import PostgresTools

load_dotenv()

from phi.storage.agent.postgres import PgAgentStorage

db_url = "postgresql://postgres:1234@localhost:5432/knowledge_base"
storage = PgAgentStorage(
    table_name="names",
    db_url=db_url,
)

postgres_tools = PostgresTools(
    host="localhost",
    port=5432,
    db_name="knowledge_base",
    user="postgres", 
    password="1234",
    run_queries=True,

)

def save_name_to_database(name: str) -> str:
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS names1 (
                name TEXT NOT NULL
            )""")
        cursor.execute("INSERT INTO names1 (name) VALUES (%s)", (name,))
        conn.commit()
        cursor.close()
        conn.close()
        return f"Successfully saved {name} to the database"
    except Exception as e:
        return f"Error saving {name} to the database: {str(e)}"


agent = Agent(
    model=Ollama(id="llama3.2"),
    name="Test Agent",
    role="Save the name directly to database",
    tools=[postgres_tools],
    storage=storage,
    show_tool_calls=True) 

# Test the agent
agent.print_response("Save this to the database tabled names, Dan Marl")