from phi.agent import Agent, AgentMemory
from phi.model.ollama import Ollama
from phi.tools import Toolkit
from phi.memory.db.postgres import PgMemoryDb
from phi.tools.sql import SQLTools
from phi.tools.postgres import PostgresTools
from knowledge_base import local_pdf_knowledge_base
# from scheduler_agent import scheduler_agent
# from clinic_agent import clinic_agent
from phi.storage.agent.postgres import PgAgentStorage
from os import getenv
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime

load_dotenv()


db_url="postgresql+psycopg://postgres:1234@localhost:5432/knowledge_base"

storage = PgAgentStorage(
    table_name="clinic_chat_sessions",
    db_url=db_url,
)
postgres_tools = PostgresTools(
    host="localhost",
    port=5432,
    db_name="knowledge_base",
    user="postgres", 
    password="1234"
)

# Database configuration
db_config = {
    'host': getenv('MYSQL_HOST'),
    'user': getenv('MYSQL_USERNAME'),
    'password': getenv('MYSQL_PASSWORD'),
    'database': getenv('MYSQL_NAME')
}

# -*- Appointment Scheduling Toolkit
class SchedulingTools(Toolkit):
    def __init__(self):
        super().__init__(name="scheduling_tools")        
        # self.register(self.parse_datetime)
        self.register(self.check_availability)
        self.register(self.create_appointment)
        
    def get_db_connection(self):
        return mysql.connector.connect(**db_config)
    
    def check_availability(self, date_time: str) -> str:
        """Check availability of a specific time slot.
        
        Args:
            date_time (str): DateTime in ISO format (YYYY-MM-DD HH:MM:SS)
            
        Returns:
            str: Available or booked status
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT appointment_id FROM appointments 
                WHERE appointment_date = %s AND status = 'scheduled'
            """, (date_time,))
            return "Booked" if cursor.fetchone() else "Available"
        finally:
            cursor.close()
            conn.close()
    
    def create_appointment(self, student_id: str, date_time: str, purpose: str) -> str:
        """Create a new appointment for a student.
        
        Args:
            student_id (str): University student ID
            date_time (str): DateTime in ISO format
            purpose (str): Reason for appointment
            
        Returns:
            str: Confirmation message or error
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            # Get user ID
            # cursor.execute("SELECT user_id FROM users WHERE student_id = %s", (student_id,))
            # user = cursor.fetchone()
            # if not user:
            #     return "Error: Student not registered"
            
            user_id = 1 # user[0]
            
            # Check availability
            # if self.check_availability(date_time) == "Booked":
            #     return "Error: Time slot already booked"
            
            # Create appointment
            cursor.execute("""
                INSERT INTO appointments (user_id, appointment_date, purpose)
                VALUES (%s, %s, %s)
            """, (user_id, date_time, purpose))
            conn.commit()
            return f"Appointment confirmed for {date_time}"
        except mysql.connector.Error as e:
            return f"Database error: {str(e)}"
        finally:
            cursor.close()
            conn.close()



scheduler_agent = Agent(
    model=Ollama(id="clinic_llama32"),
    tools=[SchedulingTools()],
    name="Scheduling Specialist",
    role="Handle appointment scheduling and availability checks",
    instructions=[
        f"You're a clinic appointment assistant. Today is {datetime.now().strftime('%B %d, %Y')}.",
        "You can help users by setting appointments at the clinic.",
        "Always confirm important details before making bookings.",
        "Appointments are 30 minutes long.",
        "Clinic hours are from 9:00 AM to 5:00 PM, Monday to Friday.",
        "If the requested time slot is not available, suggest alternative available slots.",
        "Use the set_clinic_appointment function to check availability and set appointments.",
    ],
)

clinic_agent = Agent(
    model=Ollama(id="clinic_llama32"),
    # knowledge_base=local_pdf_knowledge_base,
    name="Clinic Advisor",
    role="Provide general clinic information and health guidance",
    instructions=[
        "Do not provide medical diagnoses",
        "For emergencies, direct to campus emergency services",
        "Refer to clinic hours and services from knowledge base",
        "Maintain calm and supportive tone"
    ]
)


agent_team = Agent(
    name="ClinicBot",
    model=Ollama(id="clinic_llama32"),
    team=[scheduler_agent, clinic_agent],
    instructions=[
        f"""
            "Your name is ClinicBOT - University Health Assistant. "You're a clinic appointment assistant. Today is {datetime.now().strftime('%B %d, %Y')}."",
            "For appointments: collect preferred date and time, and purpose",
            "Always check availability before confirming",
            "For medical questions: provide general advice then recommend in-person consultation",
            "Maintain strict privacy compliance with all student data"
            "Provide information, suggestions, and support for general health inquiries inside only in the Philippines"
        """
        ],
    memory=AgentMemory(
        db=PgMemoryDb(table_name="agent_memory",
        db_url=db_url), 
        create_user_memories=True, 
        create_session_summary=True
    ),
    debug_mode=True,
    add_history_to_messages=True,
    update_user_memories_after_run=True,
    update_session_summary_after_run=True,
    knowledge=local_pdf_knowledge_base,
    search_knowledge=True,
    show_tool_calls=True,
    storage=storage,
    read_chat_history=True,
)
agent_team.knowledge.load(recreate=False)

