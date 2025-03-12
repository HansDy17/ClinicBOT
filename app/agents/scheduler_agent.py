from phi.agent import Agent
from phi.model.ollama import Ollama
from phi.tools import Toolkit
from phi.storage.agent.postgres import PgAgentStorage
from os import getenv
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime, timedelta
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
        self.required_fields = ['user_id', 'date_time', 'purpose']
        self.register(self.get_db_connection)
        self.register(self.get_available_slots)
        self.register(self.is_conflict)
        self.register(self.suggest_alternative_slot)
        self.register(self.has_existing_appointment)
        self.register(self.create_appointment)
        self.register(self.cancel_appointment)
        self.register(self.reschedule_appointment)

    def get_db_connection(self):
        return mysql.connector.connect(
            host=getenv('MYSQL_HOST'),
            user=getenv('MYSQL_USERNAME'),
            password=getenv('MYSQL_PASSWORD'),
            database=getenv('MYSQL_NAME')
        )

    def get_available_slots(self):
        """Fetch available dates and times for scheduling"""
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT date_time FROM appointments1 ORDER BY date_time")
        booked_slots = {row['date_time'] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        today = datetime.today()
        available_slots = []
        for day in range(7):  
            for hour in range(8, 17):  
                slot = datetime(today.year, today.month, today.day, hour, 0) + timedelta(days=day)
                if slot not in booked_slots:
                    available_slots.append(slot.strftime("%Y-%m-%d %H:%M"))
        
        return available_slots

    def is_conflict(self, date_time: str) -> bool:
        """Check if the given date and time is already booked"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM appointments1 WHERE date_time = %s", (date_time,))
        conflict = cursor.fetchone()[0] > 0
        
        cursor.close()
        conn.close()
        return conflict

    def suggest_alternative_slot(self, date_time: str) -> str:
        """Suggests an alternative date/time if the requested slot is unavailable"""
        parsed_date = dateparser.parse(date_time)
        if not parsed_date:
            return "Invalid date format. Please try again."

        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        for i in range(1, 5):  
            new_date = parsed_date + timedelta(minutes=30 * i)
            cursor.execute("SELECT COUNT(*) FROM appointments1 WHERE date_time = %s", (new_date,))
            if cursor.fetchone()[0] == 0:
                cursor.close()
                conn.close()
                return new_date.strftime("%Y-%m-%d %H:%M")
        
        cursor.close()
        conn.close()
        return "No available slots within the next 2 hours."

    def has_existing_appointment(self, user_id: str) -> bool:
        """Check if the user already has an upcoming appointment"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM appointments1 WHERE user_id = %s AND date_time >= NOW()", (user_id,))
        existing_appointment = cursor.fetchone()[0] > 0
        
        cursor.close()
        conn.close()
        return existing_appointment

    def cancel_appointment(self, user_id: str) -> str:
        """Cancel the user's existing appointment"""
        if not self.has_existing_appointment(user_id):
            return "You don't have any upcoming appointments to cancel."
        
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM appointments1 WHERE user_id = %s AND date_time >= NOW()", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return "Your appointment has been successfully canceled."

    def reschedule_appointment(self, user_id: str, new_date_time: str) -> str:
        """Reschedule the user's appointment by canceling the old one first"""
        if not self.has_existing_appointment(user_id):
            return "You don't have an appointment to reschedule. Please book a new one."

        if self.is_conflict(new_date_time):
            alternative = self.suggest_alternative_slot(new_date_time)
            return f"That slot is already booked. Suggested alternative: {alternative}"

        self.cancel_appointment(user_id)

        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO appointments1 (user_id, date_time) VALUES (%s, %s)", (user_id, new_date_time))
        conn.commit()
        cursor.close()
        conn.close()

        return f"✅ Your appointment has been rescheduled to {new_date_time}."

    def create_appointment(self, user_id: str, date_time: str, purpose: str) -> str:
        """Create a new appointment if the user doesn't already have one"""
        if self.has_existing_appointment(user_id):
            return "You already have an existing appointment. Please cancel it before scheduling a new one."
        
        if self.is_conflict(date_time):
            alternative = self.suggest_alternative_slot(date_time)
            return f"That slot is already booked. Suggested alternative: {alternative}"
        
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO appointments1 (user_id, purpose, date_time) VALUES (%s, %s, %s)", (user_id, purpose, date_time))
        conn.commit()
        cursor.close()
        conn.close()

        return f"✅ Appointment confirmed for {date_time} with purpose: {purpose}"

agent_test = Agent(
    name="ClinicBot",
    model=Ollama(id="clinic_llama32"),
    tools=[SchedulingTools()],
    role="Handle appointment scheduling.",
    instructions=[
        f"""
            "Your name is ClinicBOT - University Health Assistant",
            "Follow this EXACT workflow for appointments:
            2. Then ask for preferred date/time
            3. Then ask for purpose
            4. Check if the user already has an appointment
            5. If the user wants to cancel, proceed with cancellation
            6. If the user wants to reschedule, cancel first, then ask for a new time
            7. Check availability, suggest alternatives if needed
            8. Confirm all details together
            9. Create appointment",
            "If the user already has an appointment, inform them and ask if they want to cancel it first.",
            "Maintain conversation context until appointment is confirmed",
            "Do not ask for specific type of doctor or specialist."
        """
    ],
    storage=storage,
    add_history_to_messages=True,
    num_history_responses=3,
    read_chat_history=True,
    debug_mode=True
)
