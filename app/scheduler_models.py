import mysql.connector
from os import getenv
from dotenv import load_dotenv  
from datetime import datetime, timedelta
import json

load_dotenv()

class Appointments(object):
    def __init__(self, id):
        self.id = id

    def get_db_connection():
        """Establish a connection to MySQL database."""
        return mysql.connector.connect(
            host = getenv('MYSQL_HOST'),
            user = getenv('MYSQL_USERNAME'),
            password = getenv('MYSQL_PASSWORD'),
            database = getenv('MYSQL_NAME')
        )

    @classmethod
    def has_existing_appointment(self, user_id):
        """Check if a user already has an upcoming appointment."""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM appointments 
            WHERE user_id = %s 
            AND appointment_date >= CURDATE()
            AND status = 'Scheduled'
        """, (user_id,))
        
        existing = cursor.fetchone()[0] > 0

        cursor.close()
        conn.close()
        return existing  # Returns True if an appointment exists, otherwise False

    @classmethod
    def get_available_slots(cls):
        """Fetch available dates and times for scheduling, skipping lunch time."""
        conn = cls.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch booked slots from the database
        cursor.execute("SELECT appointment_date, appointment_time FROM appointments ORDER BY appointment_date")
        booked_slots = {f"{row['appointment_date']} {row['appointment_time']}" for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()

        today = datetime.today()
        available_slots = []

        for day in range(7):  # Generate slots for the next 7 days
            current_date = today + timedelta(days=day)
            formatted_date = current_date.strftime("%Y-%m-%d")

            for hour in range(9, 16):  # Clinic open from 9 AM to 4 PM
                if hour == 12:  # Skip lunch break (12 PM - 1 PM)
                    continue

                slot = datetime(current_date.year, current_date.month, current_date.day, hour, 0)
                slot_str = slot.strftime("%Y-%m-%d %H:%M")

                if slot_str not in booked_slots:  # Only include available slots
                    available_slots.append({"date": formatted_date, "time": slot.strftime("%H:%M")})

        return json.dumps(available_slots)  # ✅ Convert list to JSON string
    
    @classmethod
    def get_existing_appointment(self, user_id):
        """Fetch a user's upcoming appointment details."""
        conn = self.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT appointment_date, appointment_time, purpose
            FROM appointments 
            WHERE user_id = %s 
            AND appointment_date >= CURDATE()
            AND status = 'Scheduled'
            ORDER BY appointment_date ASC
            LIMIT 1
        """, (user_id,))
        
        appointment = cursor.fetchone()
        cursor.close()
        conn.close()
        return appointment

    @classmethod
    def is_conflict(self, date, time):
        """Check if the given date and time is already booked."""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM appointments 
            WHERE appointment_date = %s AND appointment_time = %s
        """, (date, time))
        
        conflict = cursor.fetchone()[0] > 0

        cursor.close()
        conn.close()
        return conflict

    @classmethod
    def suggest_alternative_slot(self, date, time):
        """Suggest the next available weekday slot if the requested time is unavailable."""
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

    @classmethod
    def create_appointment(self, user_id, user_name, user_email, date, time, purpose):
        """Create a new appointment."""
        if self.has_existing_appointment(user_id):
            return "You already have an appointment. Please reschedule or cancel it before booking a new one."

        if self.is_conflict(date, time):
            alternative = self.suggest_alternative_slot(date, time)
            return f"That slot is already booked. Suggested alternative: {alternative}"

        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO appointments (user_id, user_name, user_email, appointment_date, appointment_time, purpose, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')
        """, (user_id, user_name, user_email, date, time, purpose))

        conn.commit()
        cursor.close()
        conn.close()

        return f"Appointment confirmed for {date} at {time}."

    @classmethod
    def cancel_appointment(self, user_id):
        """Cancel the user's existing appointment."""
        if not self.has_existing_appointment(user_id):
            return "You don't have an active appointment to cancel."

        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE appointments 
            SET status = 'Cancelled'
            WHERE user_id = %s 
            AND appointment_date >= CURDATE()
        """, (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()

        return "Your appointment has been successfully canceled."

    @classmethod
    def reschedule_appointment(self, user_id, new_date, new_time):
        """Cancel existing appointment before rescheduling."""
        
        # Check if the user has an existing appointment
        if not self.has_existing_appointment(user_id):
            return "You don't have an appointment to reschedule. Please book a new one."

        # Cancel the existing appointment
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE appointments 
            SET status = 'Cancelled'
            WHERE user_id = %s 
            AND appointment_date >= CURDATE()
        """, (user_id,))
        
        conn.commit()

        # Check if the new slot is available
        if self.is_conflict(new_date, new_time):
            alternative = self.suggest_alternative_slot(new_date, new_time)
            return f"That slot is already booked. Suggested alternative: {alternative}"

        # Schedule the new appointment
        cursor.execute("""
            INSERT INTO appointments (user_id, appointment_date, appointment_time, status)
            VALUES (%s, %s, %s, 'Scheduled')
        """, (user_id, new_date, new_time))

        conn.commit()
        cursor.close()
        conn.close()

        return f"Your appointment has been successfully rescheduled to {new_date} at {new_time}."
