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
        self.required_fields = ['appointment_date', 'appointment_time', 'purpose']
        self.register(self.get_available_slots)
        self.register(self.is_conflict)
        self.register(self.suggest_alternative_slot)
        self.register(self.has_existing_appointment)
        self.register(self.create_appointment)
        self.register(self.cancel_appointment)
        self.register(self.reschedule_appointment)
        self.register(self.is_weekday)
        self.register(self.get_next_weekday)

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
        
        cursor.execute("SELECT appointment_date FROM appointments ORDER BY appointment_date")
        booked_slots = {row['appointment_date'] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        today = datetime.today()
        available_slots = []
        for day in range(7):  
            for hour in range(8, 17):  
                slot = datetime(today.year, today.month, today.day, hour, 0) + timedelta(days=day)
                if slot not in booked_slots:
                    available_slots.append(slot.strftime("%Y-%m-%d %H:%M"))
        
        formatted_slots = "\n".join(available_slots)  # Join list into a single string
        
        return formatted_slots
    
    def is_weekday(date_str: str) -> bool:
        """Check if a given date falls on a weekday (Monday to Friday)."""
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.weekday() < 5  # Monday to Friday (0-4)
    
    def get_next_weekday(self, date_str: str) -> str:
        """Finds the next weekday if the given date falls on a weekend."""
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        while date_obj.weekday() >= 5:  # If it's Saturday (5) or Sunday (6)
            date_obj += timedelta(days=1)
        return date_obj.strftime("%Y-%m-%d")

    def is_conflict(self, date_time: str) -> bool:
        """Check if the given date and time is already booked"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Convert date_time string to date and time components
        parsed_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        appointment_date = parsed_datetime.date()
        appointment_time = parsed_datetime.time()

        # Check if the date and time already exist in the database
        cursor.execute("""
            SELECT COUNT(*) FROM appointments 
            WHERE appointment_date = %s AND appointment_time = %s
        """, (appointment_date, appointment_time))
        
        conflict = cursor.fetchone()[0] > 0

        cursor.close()
        conn.close()
        return conflict

    def suggest_alternative_slot(self, date: str, time: str) -> str:
        """Suggests the next available weekday slot if the requested time is unavailable or falls on a weekend."""
        
        parsed_date = datetime.strptime(date, "%Y-%m-%d")

        # Move to the next available weekday
        while parsed_date.weekday() >= 5:  # If it's Saturday (5) or Sunday (6)
            parsed_date += timedelta(days=1)

        conn = self.get_db_connection()
        cursor = conn.cursor()

        for i in range(1, 5):
            new_time = (datetime.strptime(time, "%H:%M") + timedelta(minutes=30 * i)).strftime("%H:%M")
            new_date_str = parsed_date.strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT COUNT(*) FROM appointments 
                WHERE appointment_date = %s AND appointment_time = %s
            """, (new_date_str, new_time))

            if cursor.fetchone()[0] == 0:
                cursor.close()
                conn.close()
                return f"{new_date_str} at {new_time}"

        cursor.close()
        conn.close()
        return "No available slots within the next 2 hours."

    def has_existing_appointment(self, user_id: str, user_name: str, user_email: str) -> str:
        """Check if the user already has an upcoming appointment and return 'Yes' or 'No'."""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Get the current date and time
        now = datetime.now()

        # Check if the user has an appointment with a date and time in the future
        cursor.execute("""
            SELECT COUNT(*) FROM appointments 
            WHERE user_id = %s 
            AND (appointment_date > %s OR (appointment_date = %s AND appointment_time >= %s))
        """, (user_id, now.date(), now.date(), now.time()))
        
        existing_appointment = cursor.fetchone()[0] > 0

        cursor.close()
        conn.close()

        return "Yes" if existing_appointment else "No"

    def cancel_appointment(self, user_id: str) -> str:
        """Cancel the user's existing appointment by updating its status to 'Cancelled'."""
        if not self.has_existing_appointment(user_id):
            return "You don't have any upcoming appointments to cancel."

        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Update the appointment status to 'Cancelled' for future appointments
        cursor.execute("""
            UPDATE appointments 
            SET status = 'Cancelled'
            WHERE user_id = %s 
            AND (appointment_date > CURDATE() OR (appointment_date = CURDATE() AND appointment_time >= CURTIME()))
        """, (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()

        return "Your appointment has been successfully canceled."

    def reschedule_appointment(self, user_id: str, user_name: str, user_email: str, date: str, time: str) -> str:
        """Reschedule an appointment only on weekdays."""

        full_datetime = dateparser.parse(f"{date} {time}")
        appointment_date = full_datetime.strftime("%Y-%m-%d")
        appointment_time = full_datetime.strftime("%H:%M:%S")  # MySQL TIME format 
        new_date = datetime.strptime(date, "%Y-%m-%d").date()
        new_time = datetime.strptime(time, "%H:%M").time()          

        # if not is_weekday(new_date):
        #     alternative_date = self.get_next_weekday(new_date)
        #     return f"Appointments can only be rescheduled to weekdays. Suggested alternative: {alternative_date} at {new_time}."

        if not self.has_existing_appointment(user_id, user_name, user_email):
            return "You don't have an appointment to reschedule. Please book a new one."

        if self.is_conflict(new_date, new_time):
            alternative = self.suggest_alternative_slot(new_date, new_time)
            return f"That slot is already booked. Suggested alternative: {alternative}"

        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE appointments 
            SET appointment_date = %s, 
                appointment_time = %s, 
                status = 'Rescheduled',
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s 
            AND (appointment_date > CURDATE() OR (appointment_date = CURDATE() AND appointment_time >= CURTIME()))
        """, (new_date, new_time, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return f"✅ Your appointment has been rescheduled to {new_date} at {new_time}."

    def create_appointment(self, user_id: str, user_name: str, user_email: str, date: str, time: str, purpose: str = "General Checkup") -> str:
        """Create a new appointment only on weekdays."""       

        # if not is_weekday(date):
        #     alternative_date = self.get_next_weekday(date)
        #     return f"Appointments can only be scheduled on weekdays. Suggested alternative: {alternative_date} at {time}."

        if self.has_existing_appointment(user_id, user_name, user_email):
            return "You already have an existing appointment. Please cancel it before scheduling a new one."

        if self.is_conflict(date, time):
            alternative = self.suggest_alternative_slot(date, time)
            return f"That slot is already booked. Suggested alternative: {alternative}"

        conn = self.get_db_connection()
        cursor = conn.cursor()

        full_datetime = dateparser.parse(f"{date} {time}")
        appointment_date = full_datetime.strftime("%Y-%m-%d")
        appointment_time = full_datetime.strftime("%H:%M:%S")  # MySQL TIME format 
        appointment_date = datetime.strptime(date, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(time, "%H:%M").time()  

        cursor.execute("""
            INSERT INTO appointments (user_id, user_name, user_email, appointment_date, appointment_time, purpose, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')
        """, (user_id, user_name, user_email, appointment_date, appointment_time, purpose))

        conn.commit()
        cursor.close()
        conn.close()

        return f"✅ Appointment confirmed for {date} at {time} with purpose: {purpose}"

user_email = "hans@gmail.com"
user_name = "Hans"
user_id = 12345     

agent_test = Agent(
    name="ClinicBot",
    model=Ollama(id="clinic_llama32"),
    tools=[SchedulingTools()],
    role="Handle appointment scheduling.",
    instructions=[
        f"""
        Your name is ClinicBOT - University Health Assistant
        Today is {datetime.now().strftime('%B %d, %Y')}.
        Follow this EXACT workflow for appointments:
        1. Use this {user_id} as the user ID, {user_name} as the user name, and {user_email} as the user email.
        2. Then ask for preferred date/time.
        3. Then ask for purpose
        4. Check the database using if the user already has an appointment
        5. If the user wants to cancel, proceed with cancellation
        6. If the user wants to reschedule, cancel first, then ask for a new time
        7. Check availability, suggest alternatives if needed
        8. Confirm all details together
        9. Convert the given date and time to a valid format date "%Y-%m-%d" and time "%H:%M"
        10. Create appointment
        """
    ],
    storage=storage,
    add_history_to_messages=True,
    num_history_responses=5,
    read_chat_history=True,
    # debug_mode=True
)