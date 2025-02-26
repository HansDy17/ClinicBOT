from phi.agent import Agent
from phi.model.ollama import Ollama
from phi.tools import Toolkit
from knowledge_base import local_pdf_knowledge_base
from phi.storage.agent.postgres import PgAgentStorage
from os import getenv
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
import dateparser

load_dotenv()

db_url = "postgresql+psycopg://postgres:1234@localhost:5432/knowledge_base"
storage = PgAgentStorage(
    table_name="clinic_chat_sessions",
    db_url=db_url,
)

# Database configuration
db_config = {
    'host': getenv('MYSQL_HOST'),
    'user': getenv('MYSQL_USERNAME'),
    'password': getenv('MYSQL_PASSWORD'),
    'database': getenv('MYSQL_NAME')
}

class SchedulingTools(Toolkit):
    def __init__(self):
        super().__init__(name="scheduling_tools")
        self.required_fields = ['student_id', 'date_time', 'purpose']
        self.register(self.get_db_connection)
        self.register(self.parse_datetime)
        self.register(self.check_availability)
        self.register(self.create_appointment)

        
    def get_db_connection(self):
        return mysql.connector.connect(
            host = getenv('MYSQL_HOST'),
            user = getenv('MYSQL_USERNAME'),
            password = getenv('MYSQL_PASSWORD'),
            database = getenv('MYSQL_NAME')
        )
    
    def parse_datetime(self, date_str: str) -> str:
        """Parse natural language datetime to ISO format"""
        parsed = dateparser.parse(
            date_str,
            settings={'PREFER_DATES_FROM': 'future'}
        )
        return parsed.strftime("%Y-%m-%d %H:%M:%S") if parsed else None
    
    def check_availability(self, date_time: str) -> str:
        """Check availability of a specific time slot"""
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
        """Create a new appointment for a student"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        # try:
        #     cursor.execute("SELECT user_id FROM users WHERE student_id = %s", (student_id,))
            # user = cursor.fetchone()
            # if not user:
            #     return "Error: Student not registered"
            
            # user_id = user[0]
            
            # if self.check_availability(date_time) == "Booked":
            #     return "Error: Time slot already booked"
            
        cursor.execute("""
            INSERT INTO appointments (user_id, appointment_date, purpose)
            VALUES (%s, %s, %s)
        """, (user_id, date_time, purpose))
        conn.commit()
        #     return f"Appointment confirmed for {date_time}"
        # except mysql.connector.Error as e:
        #     return f"Database error: {str(e)}"
        # finally:
        cursor.close()
        conn.close()

agent_team = Agent(
    name="ClinicBot",
    model=Ollama(id="clinic_llama32"),
    tools=[SchedulingTools()],
    role="Handle appointment scheduling and availability checks and give general information for university health services.",
    instructions=[
        f"""
            "Your name is ClinicBOT - University Health Assistant",
            "Follow this EXACT workflow for appointments:
            2. Then ask for preferred date/time
            3. Then ask for purpose
            4. Confirm all details together
            5. Check availability
            6. Create appointment",
            "If any information is missing, ask specifically for that information",
            "Convert dates to ISO format immediately using parse_datetime tool",
            "Confirm availability before finalizing",
            "Maintain conversation context until appointment is confirmed"
        """
    ],
    storage=storage,
    read_chat_history=True,
    debug_mode=True
)

def handle_conversation():
    print("ClinicBOT: Welcome to University Health Services. How can I help you today?")
    conversation_state = {}
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
                
            if not user_input:
                print("ClinicBOT: Please provide more details about your request.")
                continue
                
            # Process input through agent team
            response = agent_team.run(user_input, conversation_state=conversation_state)
            
            # Extract content from RunResponse
            bot_response = response.content if response.content else "I'm sorry, I didn't understand that. Could you please rephrase?"
            
            # Handle conversation state
            if "student_id" not in conversation_state:
                print(f"\nClinicBOT: {bot_response}\nCould I please get your student ID?")
            elif "date_time" not in conversation_state:
                print(f"\nClinicBOT: {bot_response}\nWhen would you like to schedule your appointment?")
            elif "purpose" not in conversation_state:
                print(f"\nClinicBOT: {bot_response}\nCould you tell me the reason for your visit?")
            else:
                print(f"\nClinicBOT: {bot_response}")
                
        except KeyboardInterrupt:
            print("\nSession ended.")
            break
        except Exception as e:
            print(f"\nClinicBOT: I encountered an error. Please try again. {str(e)}")

if __name__ == "__main__":
    handle_conversation()